import copy
import unittest
from audit_scene_benchmark_v239 import audit

class SceneBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.a={'run_id':'a','source_hash':'src','skill_hash':'v238','output_hash':'outa','scene_id':'s1','asset_hash':'asset','conditions':{'model':'x'},'shots':[{'shot_id':'s01','description':'Reaction to sound','source_beat_id':'b1'}]}
        self.b=copy.deepcopy(self.a);self.b.update(run_id='b',skill_hash='v239',output_hash='outb')
    def runaudit(self,**changes):
        d={'baseline':copy.deepcopy(self.a),'candidate':copy.deepcopy(self.b)};d.update(changes);return audit(d)
    def test_missing(self):self.assertEqual(audit({})['status'],'NOT_RUN')
    def test_structure(self):self.assertEqual(self.runaudit()['status'],'STRUCTURE_ONLY')
    def test_review(self):self.assertEqual(self.runaudit(blind_review={'reviewer_id':'r','independent':True,'scores':{'drama':4}})['status'],'REVIEW_RECORDED_NOT_ART_PROVEN')
    def test_not_independent(self):self.b['run_id']='a';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_source_mismatch(self):self.b['source_hash']='other';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_asset_mismatch(self):self.b['asset_hash']='other';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_condition_mismatch(self):self.b['conditions']['model']='other';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_same_skill(self):self.b['skill_hash']='v238';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_same_output(self):self.b['output_hash']='outa';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_duplicate_shots(self):self.b['shots'].append(copy.deepcopy(self.b['shots'][0]));self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_missing_description(self):self.b['shots'][0]['description']='';self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_empty_shots(self):self.b['shots']=[];self.assertEqual(self.runaudit()['status'],'INCOMPARABLE')
    def test_no_independent_review(self):self.assertEqual(self.runaudit(blind_review={'reviewer_id':'r','independent':False,'scores':{'drama':4}})['status'],'STRUCTURE_ONLY')
if __name__=='__main__':unittest.main()
