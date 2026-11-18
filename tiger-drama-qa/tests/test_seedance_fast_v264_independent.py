import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_seedance_fast_v264_independent import audit


def sample():
    return {'intent':'seedance_prompt','delivery_type':'seedance_prompt','delivery_status':'CANDIDATE',
            'channel':{'platform':'jimeng_web','model_display_name':'Seedance 2 Fast','proof_scope':'unknown'},
            'duration_policy':{'selected_seconds':6,'origin':'dramatic_pacing'},
            'editorial_shots':[{'id':'SH01'}],
            'takes':[{'id':'T01','shot_ids':['SH01'],'grouping':'SINGLE','generated_seconds':6,
                      'visible_payoffs':[{'shot_id':'SH01','at_seconds':5,'visible_result':'蓝色瞳孔和蓝色头发均完成可见的状态转变'}],
                      'prompt':'从惊恐、呼吸急促到眼瞳与发色渐变为蓝色，固定中近景，人物最后抬起头。'}]}

class QAIndependentV264(unittest.TestCase):
    def test_baseline(self):self.assertEqual(audit(sample())['status'],'TEXT_STRUCTURE_PASS')
    def test_payoff_trimmed(self):
        x=sample();t=x['takes'][0];t['generated_seconds']=8;t['edit_out_seconds']=6;t['visible_payoffs'][0]['at_seconds']=7
        self.assertIn('QA264-PAYOFF-TRIMMED',str(audit(x)['errors']))
    def test_duration_mismatch(self):
        x=sample();x['duration_policy']['selected_seconds']=15
        self.assertIn('QA264-FINAL-CUT-LENGTH',str(audit(x)['errors']))
    def test_wrong_fast_variant(self):
        x=sample();x['channel']['model_display_name']='Seedance 2.5 Fast'
        self.assertIn('QA264-EXACT-FAST-MODEL',str(audit(x)['errors']))
    def test_description_no_video(self):
        x={'intent':'description','delivery_type':'description','duration_policy':{'selected_seconds':None},'takes':[]}
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_unsupported_styling(self):
        x=sample();x['narrative_style']='PUPPET_MODERATE'
        self.assertIn('QA264-STYLE-AUTHORISATION',str(audit(x)['errors']))
    def test_unauthorised_poetry(self):
        x=sample();x['takes'][0]['prompt']+=' 诗号：独步天地无人识。'
        self.assertIn('QA264-UNAUTHORISED-VOICE',str(audit(x)['errors']))
    def test_truly_approved_poetry(self):
        x=sample();x['takes'][0]['source_approved_voiceover']=True;x['takes'][0]['prompt']+=' 诗号：独步天地无人识。'
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')
    def test_split_valid_seven_seconds(self):
        x=sample();x['duration_policy']['selected_seconds']=7;x['post_units']=[{'duration_seconds':1}]
        self.assertEqual(audit(x)['status'],'TEXT_STRUCTURE_PASS')

if __name__=='__main__':unittest.main()
