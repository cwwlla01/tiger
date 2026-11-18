import copy
import unittest
from audit_ensemble_camera_v232 import audit

BASE = {"scene_id":"SC01","beat_id":"B01","speaking_character":"A","dramatic_controller":"B","attention_target":"B","relationship_shift":"NONE","gaze_axis":"A left B right","camera_choice":"HOLD","cut_motivation":"NONE","reaction_beat":"B looks away","exit_state":"A left B right"}
def pair(): return {"director":[copy.deepcopy(BASE)],"video":[copy.deepcopy(BASE)]}
def codes(r): return {i["code"] for i in r["issues"]}
class EnsembleTest(unittest.TestCase):
    def test_valid(self): self.assertEqual(audit(pair())["status"],"PASS_STRUCTURAL")
    def test_missing_pair(self): self.assertEqual(audit({})["status"],"NOT_VERIFIED")
    def test_empty_pair(self): self.assertEqual(audit({"director":[],"video":[]})["status"],"NOT_VERIFIED")
    def test_missing_field(self):
        p=pair();del p["video"][0]["gaze_axis"];self.assertIn("MISSING_FIELD",codes(audit(p)))
    def test_controller_drift(self):
        p=pair();p["video"][0]["dramatic_controller"]="A";self.assertIn("FIELD_DRIFT",codes(audit(p)))
    def test_speaker_drift(self):
        p=pair();p["video"][0]["speaking_character"]="B";self.assertIn("FIELD_DRIFT",codes(audit(p)))
    def test_axis_drift(self):
        p=pair();p["video"][0]["gaze_axis"]="reversed";self.assertIn("FIELD_DRIFT",codes(audit(p)))
    def test_unmotivated_cut(self):
        p=pair();p["director"][0]["camera_choice"]="CUT";self.assertIn("UNMOTIVATED_CUT",codes(audit(p)))
    def test_motivated_cut(self):
        p=pair()
        for side in ("director","video"):
            p[side][0]["camera_choice"]="CUT";p[side][0]["cut_motivation"]="reveal B reaction"
        self.assertEqual(audit(p)["status"],"PASS_STRUCTURAL")
    def test_duplicate(self):
        p=pair();p["director"].append(copy.deepcopy(BASE));self.assertIn("DUPLICATE_BEAT",codes(audit(p)))
    def test_missing_video(self):
        p=pair();p["video"][0]["beat_id"]="B02";self.assertIn("MISSING_VIDEO_BEAT",codes(audit(p)))
    def test_unauthorized_video(self):
        p=pair();p["video"].append({**BASE,"beat_id":"B02"});self.assertIn("UNAUTHORIZED_VIDEO_BEAT",codes(audit(p)))
if __name__=="__main__": unittest.main()
