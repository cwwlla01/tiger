import unittest
from copy import deepcopy
from audit_camera_judgment_v228 import audit

class CameraJudgmentTests(unittest.TestCase):
    def setUp(self):
        self.a = {"decision_id":"D1", "chosen_design_id":"C1", "beat_id":"B1", "source_anchor":"01:12", "shot_function":"BUILD_TENSION", "dramatic_intent":"等待威胁", "attention_target":"门缝", "camera_choice":{"mode":"STATIC", "reason":"压迫", "observable_payoff":"门缝变暗"}}
        self.data = {"03":[self.a], "04":[{k:v for k,v in self.a.items() if k in ("decision_id","chosen_design_id","beat_id","shot_function","dramatic_intent","attention_target")} | {"camera_mode":"STATIC"}], "05":[]}
        self.data["05"] = deepcopy(self.data["04"])
    def check(self,code,change):
        d=deepcopy(self.data);change(d);self.assertTrue(any(x.startswith(code) for x in audit(d)),audit(d))
    def test_valid(self): self.assertEqual(audit(self.data),[])
    def test_missing_03(self): self.assertEqual(audit({}),["MISSING_03"])
    def test_missing_source(self): self.check("MISSING_SOURCE",lambda d:d["03"][0].pop("source_anchor"))
    def test_invalid_function(self): self.check("INVALID_SHOT_FUNCTION",lambda d:d["03"][0].update(shot_function="SHOW_OFF"))
    def test_missing_reason(self): self.check("MISSING_CAMERA_RATIONALE",lambda d:d["03"][0]["camera_choice"].update(reason=""))
    def test_decision_drift(self): self.check("DRIFT:04",lambda d:d["04"][0].update(chosen_design_id="C2"))
    def test_attention_drift(self): self.check("DRIFT:05",lambda d:d["05"][0].update(attention_target="怪物"))
    def test_mode_drift(self): self.check("CAMERA_MODE_DRIFT",lambda d:d["05"][0].update(camera_mode="MOVE"))
    def test_static_movement(self): self.check("UNAUTHORIZED_CAMERA_MOTION",lambda d:d["05"][0].update(dynamic_camera=True))
    def test_missing_stage(self): self.check("MISSING_STAGE:04",lambda d:d.pop("04"))
    def test_missing_decision(self): self.check("MISSING_DECISION:05",lambda d:d["05"].clear())
    def test_cut_as_take(self):
        d=deepcopy(self.data);d["03"][0]["camera_choice"]["mode"]="CUT";d["04"][0]["camera_mode"]="CUT";d["05"][0].update(camera_mode="CUT",continuous_take=True)
        self.assertIn("CUT_AS_CONTINUOUS_TAKE:D1",audit(d))

if __name__ == "__main__": unittest.main()
