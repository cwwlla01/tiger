import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_seedance_fast_v266_independent import review as audit

HERE=Path(__file__).parent/'fixtures-v266'
BAD_SCRIPT='眼瞳由原先的颜色变为清晰的蓝色。紧接着蓝色从发根沿整头发丝蔓延，头发完全转为蓝色'
BAD_REVERSED='头发完全转为蓝色。紧接着蓝色从发根沿整头发丝蔓延，眼瞳由原先的颜色变为清晰的蓝色'

class V266Independent(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.directory=Path(temp.name)
        for name in ('01.md','03.md'):
            (self.directory/name).write_bytes((HERE/name).read_bytes())
        self.doc=self.load('single.json')
        self.two=self.load('two.json')
    def load(self,name):
        data=json.loads((HERE/name).read_text(encoding='utf-8'))
        for kind in ('source_document','director_document'):
            if kind in data:data[kind]['path']=str(self.directory/data[kind]['path'])
        return data
    def must_fail(self,doc,code):
        result=audit(doc)
        self.assertEqual(result['status'],'FAIL',result)
        self.assertIn(code,str(result['errors']))
    def test_real_single_sh_order(self):self.assertEqual(audit(self.doc)['status'],'TEXT_STRUCTURE_PASS',audit(self.doc))
    def test_real_two_take_state(self):self.assertEqual(audit(self.two)['status'],'TEXT_STRUCTURE_PASS',audit(self.two))
    def test_reversed_prompt_with_all_quotes_present_fails(self):
        p=copy.deepcopy(self.doc)
        self.assertIn(BAD_SCRIPT,p['takes'][0]['prompt'])
        p['takes'][0]['prompt']=p['takes'][0]['prompt'].replace(BAD_SCRIPT,BAD_REVERSED)
        self.must_fail(p,'QA266-05-ORDER-MISMATCH')
    def test_reversed_03_order_fails_even_if_05_is_correct(self):
        p=copy.deepcopy(self.doc)
        d=self.directory/'03.md'
        content=d.read_text(encoding='utf-8')
        self.assertIn('眼瞳转蓝→头发从发根转蓝',content)
        d.write_text(content.replace('眼瞳转蓝→头发从发根转蓝','头发从发根转蓝→眼瞳转蓝'),encoding='utf-8')
        p['director_document']['sha256']=hashlib.sha256(d.read_bytes()).hexdigest()
        self.must_fail(p,'QA266-03-ORDER-MISMATCH')
    def test_01_order_drift_detected_after_source_hash_updated(self):
        p=copy.deepcopy(self.doc)
        f=self.directory/'01.md'
        src=f.read_text(encoding='utf-8')
        a=src.index('△他的身体突然僵住')
        b=src.index('△蓝色从发根')
        c=src.index('△泪痕仍留在脸上')
        f.write_text(src[:a]+src[b:c]+src[a:b]+src[c:],encoding='utf-8')
        p['source_document']['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
        self.must_fail(p,'QA266-01-ORDER-MISMATCH')
    def test_sequence_manifest_missing_fails(self):
        p=copy.deepcopy(self.doc);p.pop('sequence_groups')
        self.must_fail(p,'QA266-MISSING-ORDER-GROUPS')
    def test_sequence_coverage_missing_hair_fails(self):
        p=copy.deepcopy(self.doc);p['sequence_groups'][0]['event_ids']=['EV-EYE']
        self.must_fail(p,'QA266-CRITICAL-EVENT-GROUP-COVERAGE')
    def test_duplicate_witness_ambiguous_fails(self):
        p=copy.deepcopy(self.doc);p['takes'][0]['prompt']+=' 眼瞳由原先的颜色变为清晰的蓝色'
        self.must_fail(p,'QA266-PROMPT-QUOTE-NOT-UNIQUE')
    def test_authorised_director_presentation_reorder_only_text_candidate(self):
        p=copy.deepcopy(self.doc)
        d=self.directory/'03.md'
        clause='\n导演呈现重排：先EV-HAIR，后EV-EYE；这是展示信息的顺序，不能改写身体真实变化因果。'
        d.write_text(d.read_text(encoding='utf-8')+clause,encoding='utf-8')
        p['director_document']['sha256']=hashlib.sha256(d.read_bytes()).hexdigest()
        p['sequence_groups'][0].update({'mode':'DIRECTOR_PRESENTATION_REORDER',
          'presentation_event_ids':['EV-HAIR','EV-EYE'],'director_order_quote':clause.strip()})
        p['takes'][0]['prompt']=p['takes'][0]['prompt'].replace(BAD_SCRIPT,BAD_REVERSED)
        result=audit(p)
        self.assertEqual(result['status'],'TEXT_STRUCTURE_PASS',result)
        self.assertIn('QA266-PRESENTATION-REORDER-REQUIRES-MANUAL-SEMANTIC-REVIEW',str(result['notices']))
    def test_reorder_without_real_03_evidence_rejected(self):
        p=copy.deepcopy(self.doc);p['sequence_groups'][0].update({'mode':'DIRECTOR_PRESENTATION_REORDER',
         'presentation_event_ids':['EV-HAIR','EV-EYE'],'director_order_quote':'导演呈现重排：先EV-HAIR，后EV-EYE。'})
        p['takes'][0]['prompt']=p['takes'][0]['prompt'].replace(BAD_SCRIPT,BAD_REVERSED)
        self.must_fail(p,'QA266-REORDER-NO-03-DIRECTIVE')
    def test_next_take_eye_color_changed_without_transition(self):
        p=copy.deepcopy(self.two);p['take_handoffs'][0]['properties'][0]['next_start_value']='BLACK'
        self.must_fail(p,'QA266-STATE-CHANGES-WITHOUT-TRANSITION')
    def test_actual_followup_prompt_resets_eye_color_fails(self):
        p=copy.deepcopy(self.two)
        p['takes'][1]['prompt']=p['takes'][1]['prompt'].replace('眼瞳仍然蓝色','眼瞳突然恢复黑色')
        self.must_fail(p,'QA266-NO-NEXT-START-TEXT')
    def test_next_take_omits_blue_hair_handoff(self):
        p=copy.deepcopy(self.two);p['take_handoffs'][0]['properties'].pop()
        self.must_fail(p,'QA266-PERSISTENT-FIELD-OMITTED')
    def test_unwitnessed_next_take_continuity(self):
        p=copy.deepcopy(self.two);p['take_handoffs'][0]['properties'][1]['next_quote']='没有写在视频提示词里的发色'
        self.must_fail(p,'QA266-NO-NEXT-START-TEXT')
    def test_false_scene_change_is_not_a_bypass(self):
        p=copy.deepcopy(self.two)
        p['take_handoffs']=[{'from_take':'T01','to_take':'T02','kind':'SCENE_CHANGE','reason':'演员走出房间开始一场新剧情，空间切换但目前没有来源证据。'}]
        self.must_fail(p,'QA266-SCENE-CHANGE-NOT-IN-01')
    def test_scene_change_must_not_erase_blue_eye_and_hair(self):
        p=copy.deepcopy(self.two)
        src=self.directory/'01.md'
        src.write_text(src.read_text(encoding='utf-8')+'\n## SC02 INT. 新房间 / 夜\n',encoding='utf-8')
        p['source_document']['sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
        p['take_handoffs']=[{'from_take':'T01','to_take':'T02','kind':'SCENE_CHANGE',
            'reason':'测试场次有明确SC02转场，但主角已经变成蓝瞳蓝发的持久状态不能自动重置。',
            'source_scene_quote':'## SC02 INT. 新房间 / 夜'}]
        self.must_fail(p,'QA266-SCENE-LOST-PERSISTENT-STATE')
    def test_real_scene_change_preserves_on_screen_blue_state(self):
        p=copy.deepcopy(self.two)
        src=self.directory/'01.md'
        src.write_text(src.read_text(encoding='utf-8')+'\n## SC02 INT. 新房间 / 夜\n',encoding='utf-8')
        p['source_document']['sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
        p['take_handoffs'][0].update({'kind':'SCENE_CHANGE',
            'reason':'有真实SC02转场，下一场同一主角仍保留蓝瞳蓝发，继续记录同一身份的永久状态。',
            'source_scene_quote':'## SC02 INT. 新房间 / 夜'})
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS',audit(p))
    def test_single_take_has_no_handoff_or_15_second_default(self):
        p=copy.deepcopy(self.doc)
        self.assertEqual(p['duration_policy']['selected_seconds'],6.5)
        p['take_handoffs']=[{'from_take':'T01','to_take':'T02'}]
        self.must_fail(p,'QA266-SPURIOUS-TAKE-BORDER')
    def test_description_does_not_enter_video_pipeline(self):
        self.assertEqual(audit({'intent':'description','delivery_type':'description','takes':[],
          'duration_policy':{'selected_seconds':None}})['status'],'TEXT_STRUCTURE_PASS')
    def test_cli_relative_source_manifest(self):
        p=copy.deepcopy(self.doc)
        p['source_document']['path']='01.md';p['director_document']['path']='03.md'
        path=self.directory/'plan.json';path.write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8')
        script=Path(__file__).resolve().parents[1]/'scripts/audit_seedance_fast_v266_independent.py'
        r=subprocess.run([sys.executable,str(script),str(path)],cwd='/',capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

if __name__=='__main__':unittest.main()
