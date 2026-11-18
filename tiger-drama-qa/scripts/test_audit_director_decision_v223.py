import unittest,copy
from audit_director_decision_v223 import audit

def valid():
 d={"decision_id":"D1","selected_candidate_id":"A","source_anchors":["S1"],"scene_goal":"Reveal threat","beat_coverage":["B1"],"style_version":"v1","candidates":[{"candidate_id":"A","hard_gate_pass":True,"veto_reasons":[],"ai_feasibility":"SUPPORTED"},{"candidate_id":"B","hard_gate_pass":False,"veto_reasons":["source"]}]}
 fields={k:copy.deepcopy(d[k]) for k in ("decision_id","selected_candidate_id","source_anchors","scene_goal","beat_coverage","style_version")}
 return {"03":d,"04":copy.deepcopy(fields),"05":copy.deepcopy(fields)}
class Tests(unittest.TestCase):
 def test_valid(self):self.assertEqual(audit(valid()),[])
 def test_missing_03(self):self.assertIn("MISSING_03",audit({}))
 def test_missing_04(self):
  x=valid();del x["04"];self.assertIn("MISSING_04",audit(x))
 def test_missing_05(self):
  x=valid();del x["05"];self.assertIn("MISSING_05",audit(x))
 def test_unknown_selection(self):
  x=valid();x["03"]["selected_candidate_id"]="Z";self.assertIn("SELECTED_NOT_FOUND",audit(x))
 def test_vetoed(self):
  x=valid();x["03"]["candidates"][0]["hard_gate_pass"]=False;self.assertIn("VETOED_SELECTED",audit(x))
 def test_unsupported(self):
  x=valid();x["03"]["candidates"][0]["ai_feasibility"]="UNSUPPORTED";self.assertIn("UNSUPPORTED_SELECTED",audit(x))
 def test_pilot_claim(self):
  x=valid();x["03"]["candidates"][0]["ai_feasibility"]="PILOT_REQUIRED";x["05"]["model_verified"]=True;self.assertIn("PILOT_MISREPRESENTED_05",audit(x))
 def test_drift(self):
  x=valid();x["04"]["scene_goal"]="Other";self.assertIn("DRIFT_04_SCENE_GOAL",audit(x))
 def test_unselected_used(self):
  x=valid();x["05"]["candidate_id"]="B";self.assertIn("UNSELECTED_USED_05",audit(x))
 def test_duplicate(self):
  x=valid();x["03"]["candidates"][1]["candidate_id"]="A";self.assertIn("DUPLICATE_OR_EMPTY_CANDIDATE",audit(x))
 def test_blocked_selection(self):
  x=valid();x["03"]["status"]="BLOCKED_REVISE";self.assertIn("BLOCKED_WITH_SELECTION",audit(x))
if __name__=="__main__":unittest.main()
