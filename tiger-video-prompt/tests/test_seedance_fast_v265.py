import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_seedance_fast_v265 import audit


class V265EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source=Path(self.temp.name)/'01.md'
        self.source.write_text('# EP01\n△眼瞳从黑色变成蓝色。\n△头发由黑转成蓝色。\n',encoding='utf-8')
        self.prompt='一个人惊恐得颤抖，突然眼瞳从黑色变成蓝色。头发由黑转成蓝色。他抬起头，蓝色双眼和蓝色头发清晰可见。'
        self.plan={
          'intent':'seedance_prompt','delivery_type':'seedance_prompt','delivery_status':'CANDIDATE',
          'channel':{'platform':'jimeng_web','model_display_name':'Seedance 2 Fast',
                     'proof_scope':'unknown','multishot_proof':'unverified','supported_durations_s':[]},
          'duration_policy':{'origin':'dramatic_pacing','selected_seconds':6,
               'reason':'恐惧、身体僵住、眼睛和头发变色、最后抬头的表演需要依次清晰显现。'},
          'editorial_shots':[{'id':'SH01'}],'narrative_style':'NATURAL',
          'source_document':{'path':str(self.source),'sha256':hashlib.sha256(self.source.read_bytes()).hexdigest()},
          'takes':[{'id':'T01','grouping':'SINGLE','shot_ids':['SH01'],'generated_seconds':6,
                    'prompt':self.prompt,'visible_payoffs':[{'shot_id':'SH01','at_seconds':5,
                        'visible_result':'蓝色眼瞳和蓝色头发均已变色并可见',
                        'prompt_quote':'蓝色双眼和蓝色头发清晰可见',
                        'source_quote':'眼瞳从黑色变成蓝色。'}]}],
          'critical_events':[{'id':'E-EYE','take_id':'T01',
                              'source_quote':'眼瞳从黑色变成蓝色。',
                              'prompt_quote':'眼瞳从黑色变成蓝色'},
                             {'id':'E-HAIR','take_id':'T01',
                              'source_quote':'头发由黑转成蓝色。',
                              'prompt_quote':'头发由黑转成蓝色'}]}
    def fail_code(self,doc,code):
        result=audit(doc)
        self.assertEqual(result['status'],'FAIL',result)
        self.assertIn(code,str(result['errors']))

    def test_valid_source_and_copy_trace(self):
        self.assertEqual(audit(self.plan)['status'],'TEXT_STRUCTURE_PASS')
    def test_lie_about_blue_eyes_and_hair_is_not_a_pass(self):
        bad=copy.deepcopy(self.plan)
        bad['takes'][0]['prompt']='这个人恐惧得发抖，突然恢复正常，黑色头发没有改变。'
        self.fail_code(bad,'V265-PAYOFF-NOT-IN-COPY')
        self.fail_code(bad,'V265-EVENT-PROMPT')
    def test_payoff_quote_must_exist_even_if_manifest_says_visible(self):
        bad=copy.deepcopy(self.plan)
        bad['takes'][0]['visible_payoffs'][0]['prompt_quote']='不在复制块中的虚构高潮画面'
        self.fail_code(bad,'V265-PAYOFF-NOT-IN-COPY')
    def test_cannot_use_boolean_only_to_approve_poetic_narrator(self):
        bad=copy.deepcopy(self.plan)
        bad['takes'][0]['source_approved_voiceover']=True
        bad['takes'][0]['prompt']+=' 旁白：觉醒的时刻终于来了。'
        self.fail_code(bad,'V265-VOICE-ORIGIN')
    def test_authorised_script_narrator_must_actually_be_in_source(self):
        bad=copy.deepcopy(self.plan)
        bad['takes'][0]['source_approved_voiceover']=True
        bad['takes'][0]['prompt']+=' 旁白：觉醒的时刻终于来了。'
        bad['takes'][0]['voiceover_evidence']={'origin':'script',
            'source_quote':'旁白：觉醒的时刻终于来了。',
            'prompt_quote':'旁白：觉醒的时刻终于来了。'}
        self.fail_code(bad,'V265-VOICE-SOURCE')
    def test_real_script_narration_is_traceable(self):
        p=copy.deepcopy(self.plan)
        line='旁白：恐惧尽头是一种新的觉醒。'
        self.source.write_text(self.source.read_text(encoding='utf-8')+line+'\n',encoding='utf-8')
        p['source_document']['sha256']=hashlib.sha256(self.source.read_bytes()).hexdigest()
        p['takes'][0]['prompt']+=' '+line
        p['takes'][0]['voiceover_evidence']={'origin':'script', 'source_quote':line,'prompt_quote':line}
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS')
    def test_source_hash_drift_is_detected(self):
        self.source.write_text(self.source.read_text(encoding='utf-8')+'changed',encoding='utf-8')
        self.fail_code(self.plan,'V265-SOURCE-HASH-DRIFT')
    def test_missing_source_quote_is_detected(self):
        p=copy.deepcopy(self.plan)
        p['critical_events'][1]['source_quote']='剧本里其实没有这句台词'
        self.fail_code(p,'V265-EVENT-SOURCE')
    def test_style_label_alone_is_not_approval(self):
        p=copy.deepcopy(self.plan)
        p['narrative_style']='PUPPET_FULL_REQUESTED'
        p['narrative_style_source']='approved_project'
        self.fail_code(p,'V265-STYLE-EVIDENCE')
    def test_unrelated_style_quote_is_not_in_source(self):
        p=copy.deepcopy(self.plan)
        p['narrative_style']='PUPPET_STRUCTURAL'
        p['narrative_style_source']='approved_project'
        p['narrative_style_evidence']={'source_quote':'此项目批准采用布袋戏式结构叙事。'}
        self.fail_code(p,'V265-STYLE-PROVENANCE')
    def test_user_current_style_claim_still_requires_human_review(self):
        p=copy.deepcopy(self.plan)
        p['narrative_style']='PUPPET_STRUCTURAL'
        p['narrative_style_source']='user_request'
        p['narrative_style_evidence']={'source_quote':'请用布袋戏结构强化这场戏。'}
        result=audit(p)
        self.assertEqual(result['status'],'TEXT_STRUCTURE_PASS')
        self.assertIn('V265-STYLE-USER-QUOTE',str(result['notices']))
    def test_critical_event_omission_no_longer_passes(self):
        p=copy.deepcopy(self.plan)
        p['takes'][0]['prompt']=p['takes'][0]['prompt'].replace('头发由黑转成蓝色。','头发仍然黑色。')
        self.fail_code(p,'V265-EVENT-PROMPT')
    def test_no_source_direct_chat_candidate_with_witness(self):
        p=copy.deepcopy(self.plan)
        p.pop('source_document')
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS')
        self.assertIn('V265-SOURCE-NOT-FILE-VERIFIED',str(audit(p)['notices']))
    def test_blank_critical_events_rejected_when_source_exists(self):
        p=copy.deepcopy(self.plan)
        p['critical_events']=[]
        self.fail_code(p,'V265-EVENT-COVERAGE')
    def test_description_stays_plain_prose(self):
        p={'intent':'description','delivery_type':'description','takes':[],
           'duration_policy':{'selected_seconds':None}}
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS')

    def test_merged_payoff_must_be_in_correct_sh(self):
        from test_seedance_fast_v264 import merged
        p=merged()
        p['takes'][0]['visible_payoffs'][0]['prompt_quote']='远景山脉微震'
        p['takes'][0]['visible_payoffs'][1]['prompt_quote']='特写岩壁隆起'
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS',audit(p))
        p['takes'][0]['visible_payoffs'][1]['prompt_quote']='远景山脉微震'
        self.fail_code(p,'V265-PAYOFF-WRONG-SHOT')

    def test_portable_relative_source_resolves_from_manifest_directory(self):
        p=copy.deepcopy(self.plan)
        planfile=Path(self.temp.name)/'test_plan.json'
        p['source_document']['path']=self.source.name
        planfile.write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8')
        script=Path(__file__).resolve().parents[1]/'scripts/audit_seedance_fast_v265.py'
        run=subprocess.run([sys.executable,str(script),str(planfile)],cwd='/',capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    def test_director_handoff_requires_real_quote_and_hash(self):
        p=copy.deepcopy(self.plan)
        d=Path(self.temp.name)/'03.md'
        d.write_text('SH01：连续中近景，眼瞳和头发由黑转为蓝色。',encoding='utf-8')
        p['director_document']={'path':str(d),'sha256':hashlib.sha256(d.read_bytes()).hexdigest()}
        p['director_shots']=[{'shot_id':'SH01','director_quote':'连续中近景，眼瞳和头发由黑转为蓝色。',
                             'prompt_quote':'眼瞳从黑色变成蓝色'}]
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS')
        d.write_text(d.read_text(encoding='utf-8')+'变更',encoding='utf-8')
        self.fail_code(p,'V265-SOURCE-HASH-DRIFT')

    def test_director_sh_invisible_in_prompt_rejected(self):
        p=copy.deepcopy(self.plan)
        d=Path(self.temp.name)/'03.md'
        d.write_text('SH01：连续中近景，眼瞳和头发由黑转为蓝色。',encoding='utf-8')
        p['director_document']={'path':str(d),'sha256':hashlib.sha256(d.read_bytes()).hexdigest()}
        p['director_shots']=[{'shot_id':'SH01','director_quote':'连续中近景，眼瞳和头发由黑转为蓝色。',
                             'prompt_quote':'镜头中有剧本没写的巨型火龙'}]
        self.fail_code(p,'V265-DIRECTOR-PROMPT')

if __name__=='__main__':unittest.main()
