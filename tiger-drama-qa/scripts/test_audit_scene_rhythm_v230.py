import unittest
from audit_scene_rhythm_v230 import audit

BASE = {"shots": [{"scene_id":"SC1","shot_id":"SH1","source_beat_ids":["B1"],"dramatic_function":"建立未知","attention_target":"门","camera_choice":"STATIC","entry_state":"closed","exit_state":"closed","cut_reason":"信息转移"},{"scene_id":"SC1","shot_id":"SH2","source_beat_ids":["B2"],"dramatic_function":"揭示","attention_target":"门缝","camera_choice":"CUT","entry_state":"closed","exit_state":"blood","cut_reason":"揭示"}],"reveal":{"reveal_beat_id":"B2","reveal_shot_id":"SH2"}}

def changed(fn):
    import copy
    x=copy.deepcopy(BASE); fn(x); return audit(x)

class SceneRhythmTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(audit(BASE)["status"],"PASS_STRUCTURAL")
    def test_no_shots(self): self.assertEqual(audit({})["status"],"NOT_VERIFIED")
    def test_missing_field(self): self.assertIn("MISSING_FIELD",[i["code"] for i in changed(lambda x:x["shots"][0].pop("cut_reason"))["issues"]])
    def test_duplicate(self): self.assertIn("DUPLICATE_SHOT",[i["code"] for i in changed(lambda x:x["shots"][1].update(shot_id="SH1"))["issues"]])
    def test_invalid_choice(self): self.assertIn("INVALID_CAMERA_CHOICE",[i["code"] for i in changed(lambda x:x["shots"][0].update(camera_choice="SPIN"))["issues"]])
    def test_invalid_beats(self): self.assertIn("INVALID_SOURCE_BEATS",[i["code"] for i in changed(lambda x:x["shots"][0].update(source_beat_ids=[]))["issues"]])
    def test_state_gap(self): self.assertIn("STATE_DISCONTINUITY",[i["code"] for i in changed(lambda x:x["shots"][1].update(entry_state="open"))["issues"]])
    def test_reveal_missing(self): self.assertIn("REVEAL_SHOT_MISSING",[i["code"] for i in changed(lambda x:x["reveal"].update(reveal_shot_id="SH9"))["issues"]])
    def test_invalid_reveal(self): self.assertIn("INVALID_REVEAL",[i["code"] for i in changed(lambda x:x.update(reveal={}))["issues"]])
    def test_invalid_shot(self): self.assertIn("INVALID_SHOT",[i["code"] for i in audit({"shots":[None]})["issues"]])
    def test_new_scene_resets_state(self): self.assertEqual(changed(lambda x:x["shots"][1].update(scene_id="SC2",entry_state="open"))["status"],"PASS_STRUCTURAL")
    def test_empty_id(self): self.assertIn("MISSING_FIELD",[i["code"] for i in changed(lambda x:x["shots"][0].update(shot_id=""))["issues"]])
