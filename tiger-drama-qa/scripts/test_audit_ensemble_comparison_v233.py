import copy
import unittest
from audit_ensemble_comparison_v233 import evaluate
class TestV233(unittest.TestCase):
 def record(self):
  s={"source_beat_id":"B1","shot_id":"S1","focus_character":"C","dramatic_function":"tension","cut_trigger":"reaction","screen_axis":"left-right","new_information":"none","duration_estimate":4}
  c={"source_sha256":"abc","asset_version":"v1","shots":[s]}
  return {"source_sha256":"abc","asset_version":"v1","candidates":{"A":copy.deepcopy(c),"B":copy.deepcopy(c)}}
 def test_structure_only(self):self.assertEqual(evaluate(self.record())["status"],"STRUCTURE_ONLY")
 def test_missing_source(self):
  r=self.record();r.pop("source_sha256");self.assertEqual(evaluate(r)["status"],"INCOMPARABLE")
 def test_missing_candidate(self):
  r=self.record();r["candidates"].pop("B");self.assertEqual(evaluate(r)["status"],"INCOMPARABLE")
 def test_input_mismatch(self):
  r=self.record();r["candidates"]["B"]["asset_version"]="v2";self.assertIn("B_INPUT_MISMATCH",evaluate(r)["errors"])
 def test_missing_shot_field(self):
  r=self.record();r["candidates"]["A"]["shots"][0].pop("cut_trigger");self.assertEqual(evaluate(r)["status"],"INCOMPARABLE")
 def test_coverage_mismatch(self):
  r=self.record();r["candidates"]["B"]["shots"][0]["source_beat_id"]="B2";self.assertIn("BEAT_COVERAGE_MISMATCH",evaluate(r)["errors"])
 def test_empty_shots(self):
  r=self.record();r["candidates"]["A"]["shots"]=[];self.assertIn("A_EMPTY_SHOTS",evaluate(r)["errors"])
 def test_review_not_proof(self):
  r=self.record();r["blind_review"]={"independent_reviewers":["R1"],"dimension_evidence":{"tension":"example"}};self.assertEqual(evaluate(r)["status"],"REVIEW_RECORDED_NOT_ART_PROVEN")
if __name__=='__main__':unittest.main()
