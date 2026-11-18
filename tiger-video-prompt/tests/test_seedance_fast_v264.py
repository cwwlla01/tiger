import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_seedance_fast_v264 import audit


def sample():
    return {'intent':'seedance_prompt','delivery_type':'seedance_prompt',
            'delivery_status':'CANDIDATE',
            'channel':{'platform':'jimeng_web','model_display_name':'Seedance 2 Fast',
                       'proof_scope':'unknown','multishot_proof':'unverified','supported_durations_s':[]},
            'duration_policy':{'selected_seconds':6,'user_requested_seconds':None,
                               'origin':'dramatic_pacing',
                               'reason':'Fear breaks into a visible eye and hair recoloring, followed by a reaction hold.'},
            'narrative_style':'NATURAL',
            'editorial_shots':[{'id':'SH01'}],
            'takes':[{'id':'T01','shot_ids':['SH01'],'grouping':'SINGLE',
                      'generated_seconds':6,'prompt':'一个人恐惧到浑身颤抖，突然僵住，眼瞳变成明亮蓝色，头发从发根到发梢变成蓝色；镜头固定并轻微靠近，最终停在发色和眼色已改变的脸上。',
                      'visible_payoffs':[{'shot_id':'SH01','at_seconds':5.2,'visible_result':'眼瞳与头发均已呈现鲜明蓝色，身体停止颤抖'}]}]}

def merged():
    x=sample()
    x['duration_policy']['selected_seconds']=8
    x['editorial_shots']=[{'id':'SH01'},{'id':'SH02'}]
    x['takes']=[{'id':'T01','shot_ids':['SH01','SH02'],'grouping':'MERGE','generated_seconds':8,
                 'prompt':'【00:00-00:03|SH01】远景山脉微震，光源和地形固定。【00:03|HARD_CUT】【00:03-00:08|SH02】特写岩壁隆起，长焦缓慢推近，夕阳方向保持不变。',
                 'merge_decision':{'benefit':'matched_visual_reveal','specific_gain':'保留两镜中同一条山脊纹理，使观众把震动和苏醒理解为同一个地形。',
                  'boundaries':[{'from':'SH01','to':'SH02','dramatic_reason':'视线从人物所见的山脉转到同一岩层异常，信息释放不重置。',
                                 'continuity_evidence':'山脉轮廓、岩石纹理、低角度夕阳和云层位置保持一致。',
                                 'risk_mitigation':'如果切换时地形重绘，只拆开第二段单独生成并用原山脉图参考。',
                                 'transition':'HARD_CUT','risk_level':'LOW','pilot_observed':False}]},
                 'shot_timeline':[{'shot_id':'SH01','start':0,'end':3},{'shot_id':'SH02','start':3,'end':8}],
                 'visible_payoffs':[{'shot_id':'SH01','at_seconds':2,'visible_result':'山脉轮廓已经出现清楚可见的轻微震动'},
                                   {'shot_id':'SH02','at_seconds':7,'visible_result':'原有山脊在同一岩层纹理中明显抬升'}]}]
    return x

class VideoV264(unittest.TestCase):
    def assert_fail(self,x,fragment):
        r=audit(x);self.assertEqual(r['status'],'FAIL',r);self.assertIn(fragment,str(r['errors']))
    def test_short_single_no_15_default(self):self.assertEqual(audit(sample())['status'],'TEXT_STRUCTURE_PASS')
    def test_even_3_seconds_not_rejected_by_legacy_minimum(self):
        x=sample();x['duration_policy']['selected_seconds']=3;x['takes'][0]['generated_seconds']=3;x['takes'][0]['visible_payoffs'][0]['at_seconds']=2.5
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_other_fast_model_not_substituted(self):
        x=sample();x['channel']['model_display_name']='Seedance 2.5 Fast'
        self.assert_fail(x,'E-MODEL')
    def test_long_final_film_uses_multiple_takes_without_scene_cap(self):
        x=sample();x['duration_policy'].update(selected_seconds=125,origin='user_requested',user_requested_seconds=125)
        x['editorial_shots']=[];x['takes']=[]
        for n in range(10):
            sh=f'SH{n+1:02d}'
            x['editorial_shots'].append({'id':sh})
            x['takes'].append({'id':f'T{n+1:02d}','shot_ids':[sh],'grouping':'SINGLE',
                              'generated_seconds':12.5,
                              'prompt':'固定景别的人物连续行动，各段独立完成视觉变化并保持空间连续。',
                              'visible_payoffs':[{'shot_id':sh,'at_seconds':12.0,
                                  'visible_result':'这一段的表演动作已有清晰可见的终态'}]})
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_single_missing_payoff_fails(self):
        x=sample();x['takes'][0]['visible_payoffs']=[];self.assert_fail(x,'V264-PAYOFF-COVERAGE')
    def test_single_payoff_trimmed_fails(self):
        x=sample();x['takes'][0]['generated_seconds']=8;x['takes'][0]['edit_out_seconds']=6;x['takes'][0]['visible_payoffs'][0]['at_seconds']=7
        self.assert_fail(x,'V264-PAYOFF-TRIM')
    def test_perfect_merged_candidate(self):self.assertEqual(audit(merged())['status'],'TEXT_STRUCTURE_PASS')
    def test_merged_payoff_after_trim_fails(self):
        x=merged();x['takes'][0]['generated_seconds']=9;x['takes'][0]['shot_timeline'][-1]['end']=9;x['takes'][0]['edit_out_seconds']=8
        x['takes'][0]['visible_payoffs'][-1]['at_seconds']=8.7
        self.assert_fail(x,'V264-PAYOFF-TRIM')
    def test_merged_without_reason_rejected(self):
        x=merged();x['takes'][0]['merge_decision']['benefit']='reduce_generation_count'
        self.assert_fail(x,'E-MERGE-BENEFIT')
    def test_17_second_film_from_two_independent_takes(self):
        x=sample();x['duration_policy'].update(selected_seconds=17,origin='user_requested',user_requested_seconds=17)
        t=copy.deepcopy(x['takes'][0]);t['id']='T02';t['shot_ids']=['SH02'];t['generated_seconds']=11;t['visible_payoffs']=[{'shot_id':'SH02','at_seconds':10.1,'visible_result':'人物转身面对危险，蓝色瞳孔与蓝发仍保持不变'}]
        x['editorial_shots'].append({'id':'SH02'});x['takes'].append(t)
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_final_duration_mismatch_fails(self):
        x=sample();x['duration_policy']['selected_seconds']=15
        self.assert_fail(x,'V264-FINAL-DURATION')
    def test_post_only_duration_counted(self):
        x=sample();x['duration_policy']['selected_seconds']=7;x['post_units']=[{'duration_seconds':1,'kind':'black'}]
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_reject_added_narrator(self):
        x=sample();x['takes'][0]['prompt']+=' 旁白：一场新的危机即将到来。'
        self.assert_fail(x,'V264-VOICEOVER')
    def test_allow_actual_approved_narrator(self):
        x=sample();x['takes'][0]['prompt']+=' 旁白：一场新的危机即将到来。'
        x['takes'][0]['source_approved_voiceover']=True
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_reject_unapproved_puppet_profile(self):
        x=sample();x['narrative_style']='PUPPET_MODERATE'
        self.assert_fail(x,'V264-STYLE-SOURCE')
    def test_allowed_approved_puppet_structure(self):
        x=sample();x['narrative_style']='PUPPET_STRUCTURAL';x['narrative_style_source']='approved_project'
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_description_route_avoids_video(self):
        x={'intent':'description','delivery_type':'description','takes':[],'duration_policy':{'selected_seconds':None}}
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')

if __name__=='__main__':unittest.main()
