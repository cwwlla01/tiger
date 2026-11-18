import unittest
from audit_editorial_selection_v236 import audit

def fixture():
    return {"required_source_beats":["B1","B2"],"shots":[
        {"shot_id":"S1","source_beat_ids":["B1"],"decision":"KEEP","reason":"orientation","dramatic_function":"SPATIAL_ORIENTATION"},
        {"shot_id":"S2","source_beat_ids":["B2"],"decision":"KEEP","reason":"payoff","dramatic_function":"REVEAL"}]}

class TestEditorialSelection(unittest.TestCase):
    def test_valid(self): self.assertEqual(audit(fixture()),[])
    def test_duplicate(self):
        d=fixture();d["shots"][1]["shot_id"]="S1";self.assertIn("SHOT_ID_INVALID",audit(d))
    def test_lost_beat(self):
        d=fixture();d["shots"][1]["decision"]="REMOVE";d["shots"][1]["replacement_shot_ids"]=["S1"];self.assertIn("SOURCE_BEAT_LOST",audit(d))
    def test_protected(self):
        d=fixture();d["shots"][0].update(decision="REMOVE",replacement_shot_ids=["S2"]);self.assertIn("PROTECTED_SHOT_REMOVED",audit(d))
    def test_protected_override(self):
        d=fixture();d["shots"][0].update(decision="REMOVE",replacement_shot_ids=["S2"],protected_override_evidence="director approved");self.assertNotIn("PROTECTED_SHOT_REMOVED",audit(d))
    def test_no_replacement(self):
        d=fixture();d["shots"][1]["decision"]="REMOVE";self.assertIn("REMOVAL_WITHOUT_REPLACEMENT",audit(d))
    def test_invalid_replacement(self):
        d=fixture();d["shots"][1].update(decision="REMOVE",replacement_shot_ids=["missing"]);self.assertIn("INVALID_REPLACEMENT",audit(d))
    def test_escalate(self):
        d=fixture();d["shots"][1]["decision"]="ESCALATE";self.assertIn("UNRESOLVED_ESCALATION",audit(d))
    def test_invalid_decision(self):
        d=fixture();d["shots"][1]["decision"]="MAGIC";self.assertIn("INVALID_DECISION",audit(d))
    def test_missing_rationale(self):
        d=fixture();d["shots"][0]["reason"]="";self.assertIn("MISSING_RATIONALE",audit(d))
    def test_missing_baseline(self):
        d=fixture();d.pop("required_source_beats");self.assertIn("MISSING_SOURCE_BASELINE",audit(d))
    def test_missing_beat_link(self):
        d=fixture();d["shots"][0]["source_beat_ids"]=[];self.assertIn("MISSING_BEAT_LINK",audit(d))
