import unittest
from audit_scene_orchestration_v235 import audit

def fixture():
    return {"scene":{"source_beat_ids":["b1","b2"],"payoff_beat_id":"b2","audience_knowledge":"AUDIENCE_FIRST"},"shots":[{"shot_id":"s1","beat_id":"b1","camera_choice":"STATIC","cut_trigger":"LOOK","sound_function":"OFFSCREEN"},{"shot_id":"s2","beat_id":"b2","camera_choice":"HOLD","cut_trigger":"REACTION","sound_function":"SILENCE"}],"compiled":[{"shot_id":"s1","beat_id":"b1","camera_choice":"STATIC","cut_trigger":"LOOK","sound_function":"OFFSCREEN"},{"shot_id":"s2","beat_id":"b2","camera_choice":"HOLD","cut_trigger":"REACTION","sound_function":"SILENCE"}]}
class TestSceneOrchestration(unittest.TestCase):
    def test_valid(self):self.assertEqual(audit(fixture())["issues"],[])
    def test_structure_only(self):self.assertEqual(audit(fixture())["status"],"STRUCTURE_ONLY")
    def test_duplicate(self):
        x=fixture();x["shots"][1]["shot_id"]="s1";self.assertIn("DUPLICATE_OR_EMPTY_SHOT_ID",audit(x)["issues"])
    def test_source_omission(self):
        x=fixture();x["scene"]["source_beat_ids"].append("b3");self.assertIn("SOURCE_BEAT_NOT_COVERED",audit(x)["issues"])
    def test_unsupported_beat(self):
        x=fixture();x["shots"][0]["beat_id"]="invented";self.assertIn("UNSUPPORTED_BEAT_ID",audit(x)["issues"])
    def test_payoff_missing(self):
        x=fixture();x["scene"]["payoff_beat_id"]="b9";self.assertIn("PAYOFF_NOT_COVERED",audit(x)["issues"])
    def test_knowledge_invalid(self):
        x=fixture();x["scene"]["audience_knowledge"]="MYSTERY";self.assertIn("UNKNOWN_KNOWLEDGE_MODE",audit(x)["issues"])
    def test_unknown_compiled(self):
        x=fixture();x["compiled"][0]["shot_id"]="s9";self.assertIn("UNKNOWN_COMPILED_SHOT",audit(x)["issues"])
    def test_missing_compiled(self):
        x=fixture();x["compiled"].pop();self.assertIn("SHOT_NOT_COMPILED",audit(x)["issues"])
    def test_camera_drift(self):
        x=fixture();x["compiled"][0]["camera_choice"]="MOVE";self.assertIn("DRIFT_CAMERA_CHOICE",audit(x)["issues"])
    def test_cut_drift(self):
        x=fixture();x["compiled"][0]["cut_trigger"]="RANDOM";self.assertIn("DRIFT_CUT_TRIGGER",audit(x)["issues"])
    def test_sound_drift(self):
        x=fixture();x["compiled"][0]["sound_function"]="NONE";self.assertIn("DRIFT_SOUND_FUNCTION",audit(x)["issues"])
if __name__=="__main__":unittest.main()
