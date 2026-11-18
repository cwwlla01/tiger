import unittest
from copy import deepcopy
from audit_scene_direction_v221 import audit

def fixture():
 s={"scene_id":"SC1","source_anchor":"01#12","scene_goal":"escape","dramatic_question":"will escape?","turning_point":"door shuts","outcome":"trapped","scene_beats":["b1","b2"],"shot_plan":[{"shot_id":"s1","covered_beats":["b1"],"function":"ESTABLISH","selection_reason":"show trap","duration_intent":"HOLD","attention_target":"door"},{"shot_id":"s2","covered_beats":["b2"],"function":"PAYOFF","selection_reason":"show consequence","duration_intent":"ACCELERATE","attention_target":"protagonist"}]}
 return {"03":s,"04":{"scene_id":"SC1","shot_plan":[{k:v for k,v in x.items() if k!="duration_intent"} for x in s["shot_plan"]]},"05":{"scene_id":"SC1","shot_plan":deepcopy(s["shot_plan"])}}
class TestSceneDirection(unittest.TestCase):
 def test_clean(self):self.assertEqual(audit(fixture()),[])
 def test_goal_missing(self):
  d=fixture();d['03']['scene_goal']='';self.assertIn('03:MISSING:scene_goal',audit(d))
 def test_beat_uncovered(self):
  d=fixture();d['03']['shot_plan'][1]['covered_beats']=[];self.assertIn('03:UNCOVERED:b2',audit(d))
 def test_unauthorized_beat(self):
  d=fixture();d['03']['shot_plan'][0]['covered_beats'].append('b3');self.assertIn('03:UNAUTHORIZED_BEAT:b3',audit(d))
 def test_no_reason(self):
  d=fixture();d['03']['shot_plan'][0]['selection_reason']='';self.assertTrue(any('selection_reason' in e for e in audit(d)))
 def test_bad_function(self):
  d=fixture();d['03']['shot_plan'][0]['function']='COOL';self.assertTrue(any('BAD_FUNCTION' in e for e in audit(d)))
 def test_bad_duration(self):
  d=fixture();d['03']['shot_plan'][0]['duration_intent']='FAST';self.assertTrue(any('BAD_DURATION' in e for e in audit(d)))
 def test_order_drift(self):
  d=fixture();d['05']['shot_plan'].reverse();self.assertIn('05:SHOT_ORDER_DRIFT',audit(d))
 def test_frame_attention_drift(self):
  d=fixture();d['04']['shot_plan'][0]['attention_target']='monster';self.assertIn('04:s1:DRIFT:attention_target',audit(d))
 def test_video_duration_drift(self):
  d=fixture();d['05']['shot_plan'][0]['duration_intent']='NORMAL';self.assertIn('05:s1:DRIFT:duration_intent',audit(d))
 def test_missing_stage(self):
  d=fixture();del d['04'];self.assertIn('04:MISSING_STAGE',audit(d))
 def test_duplicate_shot(self):
  d=fixture();d['03']['shot_plan'][1]['shot_id']='s1';self.assertIn('03:DUPLICATE_SHOT',audit(d))
if __name__=='__main__':unittest.main()
