import copy,json,unittest
from pathlib import Path
from audit_scene_pilot_v242 import audit
F=Path(__file__).parent/'fixtures/frozen_scene_pilot_v242.json'
class TestScenePilotV242(unittest.TestCase):
    def setUp(self):self.data=json.loads(F.read_text(encoding='utf-8'))
    def test_fixture_demo_only(self):self.assertEqual(audit(self.data)['status'],'DEMO_ONLY')
    def test_never_artistic_winner(self):self.assertIsNone(audit(self.data)['artistic_winner'])
    def test_no_real_ab_claim(self):self.assertFalse(audit(self.data)['real_version_ab_proven'])
    def test_two_metrics(self):self.assertEqual(len(audit(self.data)['metrics']),2)
    def test_missing_beat(self):
        d=copy.deepcopy(self.data);d['candidates'][0]['shots'][-1]['beat_ids']=['B3'];self.assertEqual(audit(d)['status'],'INVALID')
    def test_unknown_beat(self):
        d=copy.deepcopy(self.data);d['candidates'][0]['shots'][0]['beat_ids']=['B99'];self.assertEqual(audit(d)['status'],'INVALID')
    def test_duplicate_shot(self):
        d=copy.deepcopy(self.data);d['candidates'][0]['shots'][1]['shot_id']='A01';self.assertEqual(audit(d)['status'],'INVALID')
    def test_missing_reason(self):
        d=copy.deepcopy(self.data);d['candidates'][1]['shots'][0]['editorial_reason']='';self.assertEqual(audit(d)['status'],'INVALID')
    def test_bad_duration(self):
        d=copy.deepcopy(self.data);d['candidates'][1]['shots'][0]['duration_s']=0;self.assertEqual(audit(d)['status'],'INVALID')
    def test_boolean_duration(self):
        d=copy.deepcopy(self.data);d['candidates'][1]['shots'][0]['duration_s']=True;self.assertEqual(audit(d)['status'],'INVALID')
    def test_missing_camera(self):
        d=copy.deepcopy(self.data);d['candidates'][1]['shots'][0]['camera']='';self.assertEqual(audit(d)['status'],'INVALID')
    def test_duplicate_candidates(self):
        d=copy.deepcopy(self.data);d['candidates'][1]['id']='A';self.assertEqual(audit(d)['status'],'INVALID')
if __name__=='__main__':unittest.main()
