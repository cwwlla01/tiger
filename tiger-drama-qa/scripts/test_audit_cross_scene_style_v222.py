import unittest
from copy import deepcopy
from audit_cross_scene_style_v222 import audit

def fixture():
 b={"bible_id":"B1","bible_version":"1","authority_anchor":"bible#3","project_id":"P","motif_registry":["M1"]}
 s={"scene_id":"SC1","source_anchor":"01#1","bible_id":"B1","bible_version":"1","style_mode":"BASELINE","style_intent":"isolation","attention_rule":"door","rhythm_rule":"slow build","motif_ids":["M1"]}
 return {"style_bible":b,"03":[s],"04":[{k:v for k,v in s.items() if k!="rhythm_rule"}],"05":[deepcopy(s)]}
class TestStyle(unittest.TestCase):
 def test_clean(self):self.assertEqual(audit(fixture()),[])
 def test_missing_authority(self):
  d=fixture();d['style_bible']['authority_anchor']='';self.assertIn('BIBLE:MISSING:authority_anchor',audit(d))
 def test_bible_version_drift(self):
  d=fixture();d['03'][0]['bible_version']='2';self.assertIn('03:SC1:BIBLE_DRIFT:bible_version',audit(d))
 def test_unapproved_motif(self):
  d=fixture();d['03'][0]['motif_ids']=['M2'];self.assertIn('03:SC1:UNAPPROVED_MOTIF:M2',audit(d))
 def test_justified_deviation(self):
  d=fixture();d['03'][0]['style_mode']='JUSTIFIED_DEVIATION';d['03'][0]['style_exception_reason']='character POV';self.assertFalse(any('UNJUSTIFIED' in e for e in audit(d)))
 def test_unjustified_deviation(self):
  d=fixture();d['03'][0]['style_mode']='JUSTIFIED_DEVIATION';self.assertIn('03:SC1:UNJUSTIFIED_DEVIATION',audit(d))
 def test_bad_mode(self):
  d=fixture();d['03'][0]['style_mode']='RANDOM';self.assertIn('03:SC1:BAD_MODE',audit(d))
 def test_frame_drift(self):
  d=fixture();d['04'][0]['attention_rule']='face';self.assertIn('04:SC1:DRIFT:attention_rule',audit(d))
 def test_video_rhythm_drift(self):
  d=fixture();d['05'][0]['rhythm_rule']='fast';self.assertIn('05:SC1:DRIFT:rhythm_rule',audit(d))
 def test_missing_stage(self):
  d=fixture();del d['05'];self.assertIn('05:MISSING_STAGE',audit(d))
 def test_scene_order_drift(self):
  d=fixture();d['04']=[];self.assertIn('04:SCENE_ORDER_DRIFT',audit(d))
 def test_duplicate_scene(self):
  d=fixture();d['03'].append(deepcopy(d['03'][0]));self.assertIn('03:DUPLICATE_SCENE',audit(d))
if __name__=='__main__':unittest.main()
