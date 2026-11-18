import unittest
from audit_execution_route_v224 import audit

def sample():
 return dict(source_anchor="01#1",scene_id="SC1",shot_id="SH1",take_id="T1",beat_ids=["B1"],authority_version="v1")
class RoutingTests(unittest.TestCase):
 def test_valid(self): self.assertEqual(audit(sample()),[])
 def test_missing_source(self):
  d=sample();del d["source_anchor"];self.assertIn("MISSING_SOURCE_ANCHOR",audit(d))
 def test_empty_take(self):
  d=sample();d["take_id"]="";self.assertIn("MISSING_TAKE_ID",audit(d))
 def test_empty_beats(self):
  d=sample();d["beat_ids"]=[];self.assertIn("INVALID_BEAT_IDS",audit(d))
 def test_wrong_beats(self):
  d=sample();d["beat_ids"]="B1";self.assertIn("INVALID_BEAT_IDS",audit(d))
 def test_blank_state(self):
  d=sample();d["end_state"]="";self.assertIn("BLANK_END_STATE",audit(d))
 def test_unknown_state_explicit(self):
  d=sample();d["end_state"]="NOT_VERIFIED";self.assertEqual(audit(d),[])
 def test_video_requires_authority(self):
  d=sample();d["stage"]="05";self.assertIn("MISSING_DIRECTOR_AUTHORITY",audit(d))
 def test_frame_requires_authority(self):
  d=sample();d["stage"]="04";self.assertIn("MISSING_DIRECTOR_AUTHORITY",audit(d))
 def test_qa_no_rewrite(self):
  d=sample();d.update(stage="06",modifies_authority=True);self.assertIn("QA_MODIFIES_AUTHORITY",audit(d))
 def test_model_claim_evidence(self):
  d=sample();d["model_verified"]=True;self.assertIn("UNSUPPORTED_MODEL_CLAIM",audit(d))
 def test_alias_trace(self):
  d=sample();d["alias_used"]="old";self.assertIn("UNTRACED_ALIAS",audit(d))
