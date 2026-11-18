import unittest
from audit_hybrid_camera_v229 import audit
BASE={"shot_id":"S1","camera_choice":"STATIC","dramatic_intent":"建立压迫","audience_information":"门内未知","attention_target":"门"}
class TestHybridCamera(unittest.TestCase):
    def check(self,change,expected):
        row={**BASE,**change}
        self.assertIn(expected,[code for _,code in audit([row])])
    def test_clean(self):self.assertEqual(audit([BASE]),[])
    def test_missing_intent(self):self.check({"dramatic_intent":""},"MISSING_DRAMATIC_INTENT")
    def test_missing_info(self):self.check({"audience_information":""},"MISSING_AUDIENCE_INFORMATION")
    def test_missing_attention(self):self.check({"attention_target":""},"MISSING_ATTENTION_TARGET")
    def test_invalid(self):self.check({"camera_choice":"ZOOM"},"INVALID_CAMERA_CHOICE")
    def test_static_to_move(self):self.check({"compiled_camera_choice":"MOVE"},"UNAUTHORIZED_CAMERA_CHANGE")
    def test_hold_to_move(self):self.check({"camera_choice":"HOLD","compiled_camera_choice":"MOVE"},"UNAUTHORIZED_CAMERA_CHANGE")
    def test_move_no_path(self):self.check({"camera_choice":"MOVE"},"MISSING_MOTION_PATH")
    def test_move_with_path(self):self.assertEqual(audit([{**BASE,"camera_choice":"MOVE","motion_path":"向前2米"}]),[])
    def test_cut_continuous(self):self.check({"camera_choice":"CUT","single_continuous_take":True},"CUT_IN_CONTINUOUS_TAKE")
    def test_early_reveal(self):self.check({"reveal_before_source":True},"PREMATURE_REVEAL")
    def test_multi(self):self.assertEqual(len(audit([BASE,{**BASE,"shot_id":"S2","reveal_before_source":True}])),1)
if __name__=="__main__":unittest.main()
