import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_writing_route_v417 import audit


def base():
    return {'user_artifact':'screenplay','delivered_artifact':'screenplay',
            'full_playable_text':True,'stageable_actions_and_dialogue':True,
            'outline_requested':False,'outline_before_script':False,'style':'NATURAL',
            'compulsory_poetry':False,'unsourced_voiceover':False}

class WriterV417(unittest.TestCase):
    def test_finished_script_default(self):self.assertEqual(audit(base())['status'],'TEXT_ROUTE_PASS')
    def test_forbidden_preoutline(self):
        x=base();x['outline_before_script']=True
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_explicit_plan_first_preserved(self):
        x=base();x['outline_requested']=True;x['outline_before_script']=True
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')
    def test_outline_only(self):
        x=base();x.update(user_artifact='outline',delivered_artifact='outline',full_playable_text=False)
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')
    def test_evaluation_only(self):
        x=base();x.update(user_artifact='evaluation',delivered_artifact='evaluation')
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')
    def test_style_not_automatically_added(self):
        x=base();x['style']='PUPPET_MODERATE'
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_approved_structural_in_modern_context(self):
        x=base();x['style']='PUPPET_STRUCTURAL';x['style_requested']=True
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')
    def test_unrequested_poem_rejected(self):
        x=base();x['compulsory_poetry']=True
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_strong_style_only_if_explicit(self):
        x=base();x['style']='PUPPET_FULL_REQUESTED';x['style_requested']=True
        self.assertEqual(audit(x)['status'],'TEXT_ROUTE_PASS')
    def test_voiceover_must_have_source(self):
        x=base();x['unsourced_voiceover']=True
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_no_automatic_screenplay_from_description(self):
        x=base();x['user_artifact']='description'
        self.assertEqual(audit(x)['status'],'FAIL')
    def test_script_beats_are_playable(self):
        x=base();x['stageable_actions_and_dialogue']=False
        self.assertEqual(audit(x)['status'],'FAIL')

if __name__=='__main__':unittest.main()
