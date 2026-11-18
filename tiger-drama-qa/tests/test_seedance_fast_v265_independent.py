import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_seedance_fast_v265_independent import audit


class IndependentV265(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.src=Path(t.name)/'01.md'
        self.src.write_text('△眼瞳变为蓝色。\n△头发变为蓝色。\n',encoding='utf-8')
        self.doc={
         'intent':'seedance_prompt','delivery_type':'seedance_prompt','delivery_status':'CANDIDATE',
         'channel':{'platform':'jimeng_web','model_display_name':'Seedance 2 Fast','proof_scope':'unknown'},
         'duration_policy':{'selected_seconds':6,'origin':'dramatic_pacing'},
         'narrative_style':'NATURAL','editorial_shots':[{'id':'SH01'}],
         'source_document':{'path':str(self.src),'sha256':hashlib.sha256(self.src.read_bytes()).hexdigest()},
         'takes':[{'id':'T01','grouping':'SINGLE','shot_ids':['SH01'],'generated_seconds':6,
                   'prompt':'镜头连续。眼瞳变为蓝色。头发变为蓝色。蓝瞳蓝发最终都可见。',
                   'visible_payoffs':[{'shot_id':'SH01','at_seconds':5,
                     'visible_result':'眼睛和头发都已经清楚转成蓝色了',
                     'prompt_quote':'蓝瞳蓝发最终都可见。',
                     'source_quote':'眼瞳变为蓝色。'}]}],
         'critical_events':[{'id':'E1','take_id':'T01','source_quote':'眼瞳变为蓝色。','prompt_quote':'眼瞳变为蓝色。'},
                           {'id':'E2','take_id':'T01','source_quote':'头发变为蓝色。','prompt_quote':'头发变为蓝色。'}]}
    def reject(self,p,code):
        r=audit(p);self.assertEqual(r['status'],'FAIL',r);self.assertIn(code,str(r['errors']))
    def test_good_trace(self):self.assertEqual(audit(self.doc)['status'],'TEXT_STRUCTURE_PASS')
    def test_fake_payoff(self):
        p=copy.deepcopy(self.doc);p['takes'][0]['prompt']='一个人吓得发抖，眼睛正常，头发黑色。'
        self.reject(p,'QA265-PAYOFF-ONLY-IN-MANIFEST')
    def test_fake_narrator_approved_flag_is_rejected(self):
        p=copy.deepcopy(self.doc);p['takes'][0]['source_approved_voiceover']=True
        p['takes'][0]['prompt']+=' 旁白：我是虚构的旁白。'
        self.reject(p,'QA265-BOOLEAN-VOICE-APPROVAL-REJECTED')
    def test_fake_style_approved_project(self):
        p=copy.deepcopy(self.doc);p['narrative_style']='PUPPET_MODERATE'
        p['narrative_style_source']='approved_project'
        p['narrative_style_evidence']={'source_quote':'项目批准使用布袋戏模式。'}
        self.reject(p,'QA265-STYLE-PROJECT-TAG-NOT-ENOUGH')
    def test_source_hash_mismatch(self):
        self.src.write_text('△眼瞳没有变色。',encoding='utf-8')
        self.reject(self.doc,'QA265-SOURCE-CHANGED')
    def test_source_quote_not_in_document(self):
        p=copy.deepcopy(self.doc);p['critical_events'][0]['source_quote']='这是剧本中不存在的桥段'
        self.reject(p,'QA265-SOURCE-EVENT-CHANGED')
    def test_wrong_payoff_witness(self):
        p=copy.deepcopy(self.doc);p['takes'][0]['visible_payoffs'][0]['prompt_quote']='无中生有的情绪高潮'
        self.reject(p,'QA265-PAYOFF-ONLY-IN-MANIFEST')
    def test_source_but_no_critical_events(self):
        p=copy.deepcopy(self.doc);p['critical_events']=[]
        self.reject(p,'QA265-SOURCE-WITHOUT-CRITICAL-EVENT-MAP')
    def test_no_source_needs_real_brief_review(self):
        p=copy.deepcopy(self.doc);p.pop('source_document')
        r=audit(p);self.assertEqual(r['status'],'TEXT_STRUCTURE_PASS')
        self.assertIn('QA265-NO-FILE-BASED-SOURCE',str(r['notices']))
    def test_plain_description_route(self):
        p={'intent':'description','delivery_type':'description','takes':[],'duration_policy':{'selected_seconds':None}}
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS')

    def test_merged_payoff_does_not_borrow_prior_sh(self):
        from test_seedance_fast_v264_independent import sample
        p=sample()
        p['editorial_shots']=[{'id':'SH01'},{'id':'SH02'}]
        t=p['takes'][0]
        t['shot_ids']=['SH01','SH02'];t['grouping']='MERGE'
        t['generated_seconds']=8
        t['prompt']='[00:00-00:03 | SH01] 室内角色惊恐。[00:03 | HARD_CUT] [00:03-00:08 | SH02] 镜头推近，蓝色头发出现。'
        t['shot_timeline']=[{'shot_id':'SH01','start':0,'end':3},{'shot_id':'SH02','start':3,'end':8}]
        t['merge_decision']={'benefit':'continuous_actor_performance','boundaries':[{
             'from':'SH01','to':'SH02','dramatic_reason':'接续同一角色恐惧变化和抬头的因果信息呈现。',
             'continuity_evidence':'角色在室内原位，空间光源、面容和衣服始终保持一致。',
             'risk_mitigation':'生成跨切口变形时拆成两段独立视频，并沿用相同定妆。',
             'risk_level':'LOW'}]}
        t['visible_payoffs']=[{'shot_id':'SH01','at_seconds':2,'visible_result':'人物恐惧得不断发抖','prompt_quote':'室内角色惊恐。'},
                              {'shot_id':'SH02','at_seconds':7,'visible_result':'镜头清晰呈现蓝色头发','prompt_quote':'室内角色惊恐。'}]
        p['duration_policy']['selected_seconds']=8
        self.reject(p,'QA265-PAYOFF-WRONG-SH')

    def test_portable_manifest_reference(self):
        p=copy.deepcopy(self.doc)
        p['source_document']['path']=self.src.name
        f=self.src.parent/'plan.json';f.write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8')
        checker=Path(__file__).resolve().parents[1]/'scripts/audit_seedance_fast_v265_independent.py'
        proc=subprocess.run([sys.executable,str(checker),str(f)],cwd='/',capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)

    def test_director_quote_must_exist_and_match_prompt(self):
        p=copy.deepcopy(self.doc)
        d=self.src.parent/'03.md'
        d.write_text('SH01：中近景一镜到底，人物蓝瞳蓝发。',encoding='utf-8')
        p['director_document']={'path':str(d),'sha256':hashlib.sha256(d.read_bytes()).hexdigest()}
        p['director_shots']=[{'shot_id':'SH01','director_quote':'中近景一镜到底，人物蓝瞳蓝发。',
                             'prompt_quote':'眼瞳变为蓝色。'}]
        self.assertEqual(audit(p)['status'],'TEXT_STRUCTURE_PASS')
        p['director_shots'][0]['prompt_quote']='实际上没有发生的动作'
        self.reject(p,'QA265-DIRECTOR-NOT-IN-COPY')

    def test_director_source_hash_drift(self):
        p=copy.deepcopy(self.doc)
        d=self.src.parent/'03.md'
        d.write_text('SH01：蓝色瞳孔的特写。',encoding='utf-8')
        p['director_document']={'path':str(d),'sha256':hashlib.sha256(d.read_bytes()).hexdigest()}
        p['director_shots']=[{'shot_id':'SH01','director_quote':'蓝色瞳孔的特写。',
                             'prompt_quote':'眼瞳变为蓝色。'}]
        d.write_text('SH01：内容已更改',encoding='utf-8')
        self.reject(p,'QA265-SOURCE-CHANGED')

if __name__=='__main__':unittest.main()
