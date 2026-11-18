import unittest,copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_frozen_scene_v240 import audit,digest

def fixture():
    a=[{'shot_id':'S1','source_beat_id':'B1','description':'enter','dramatic_function':'setup','cut_trigger':'look'},{'shot_id':'S2','source_beat_id':'B2','description':'pause','dramatic_function':'suspense','cut_trigger':'sound'}]
    b=[{'shot_id':'T1','source_beat_id':'B1','description':'enter wider','dramatic_function':'setup','cut_trigger':'look'},{'shot_id':'T2','source_beat_id':'B2','description':'hold reaction','dramatic_function':'suspense','cut_trigger':'sound'}]
    def run(id,skill,shots):return {'run_id':id,'scene_id':'SC1','source_hash':'source','asset_hash':'asset','skill_hash':skill,'conditions':{'model':'fixed'},'shots':shots,'output_hash':digest(shots)}
    return {'frozen_beats':['B1','B2'],'baseline':run('a','v238',a),'candidate':run('b','v239',b)}

class FrozenSceneTests(unittest.TestCase):
    def test_valid_structure(self):self.assertEqual(audit(fixture())['status'],'STRUCTURE_ONLY')
    def test_not_run(self):self.assertEqual(audit({})['status'],'NOT_RUN')
    def test_missing_beat(self):
        d=fixture();d['candidate']['shots'].pop();d['candidate']['output_hash']=digest(d['candidate']['shots']);self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_extra_beat(self):
        d=fixture();d['candidate']['shots'][1]['source_beat_id']='B3';d['candidate']['output_hash']=digest(d['candidate']['shots']);self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_hash_tampering(self):
        d=fixture();d['candidate']['shots'][0]['description']='tampered';self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_duplicate_shot(self):
        d=fixture();d['candidate']['shots'][1]['shot_id']='T1';d['candidate']['output_hash']=digest(d['candidate']['shots']);self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_same_run(self):
        d=fixture();d['candidate']['run_id']='a';self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_different_source(self):
        d=fixture();d['candidate']['source_hash']='other';self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_different_assets(self):
        d=fixture();d['candidate']['asset_hash']='other';self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_different_conditions(self):
        d=fixture();d['candidate']['conditions']={'model':'other'};self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_same_skill(self):
        d=fixture();d['candidate']['skill_hash']='v238';self.assertEqual(audit(d)['status'],'INCOMPARABLE')
    def test_review_recorded(self):
        d=fixture();d['blind_review']={'independent':True,'reviewer_id':'blind1','scores':{'a':3,'b':4},'rationale':'observed'};self.assertEqual(audit(d)['status'],'REVIEW_RECORDED_NOT_ART_PROVEN')
    def test_incomplete_review(self):
        d=fixture();d['blind_review']={'independent':True,'reviewer_id':'blind1','scores':{'a':3}};self.assertEqual(audit(d)['status'],'STRUCTURE_ONLY')
