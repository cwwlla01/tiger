import unittest
from audit_emotional_tempo_v237 import audit

BASE={"shot_id":"SH01","beat_id":"B01","tension_intent":"HOLD","attention_target":"door","knowledge_mode":"CHARACTER_AHEAD","edit_duration_s":"2-4","cut_trigger":"reaction","sound_role":"OFFSCREEN","protected_hold":True,"hold_reason":"dread"}
class TempoTests(unittest.TestCase):
    def test_pass(self):self.assertEqual(audit([BASE],[BASE])["status"],"STRUCTURE_PASS_ONLY")
    def test_missing_authority(self):self.assertEqual(audit(None,[BASE])["status"],"NOT_VERIFIED")
    def test_missing_compiled(self):self.assertEqual(audit([BASE],None)["status"],"NOT_VERIFIED")
    def test_invalid_input(self):self.assertIn("INVALID_INPUT_TYPE",audit({},[])["issues"])
    def test_missing_shot(self):self.assertIn("MISSING_SHOT:SH01",audit([BASE],[])["issues"])
    def test_extra_shot(self):self.assertIn("UNAUTHORIZED_SHOT:SH02",audit([BASE],[BASE,{"shot_id":"SH02"}])["issues"])
    def test_duplicate_director(self):self.assertIn("INVALID_DIRECTOR_SHOT_IDS",audit([BASE,BASE],[BASE])["issues"])
    def test_duplicate_compiled(self):self.assertIn("DUPLICATE_COMPILED_SHOT",audit([BASE],[BASE,BASE])["issues"])
    def test_duration_drift(self):self.assertIn("DRIFT_edit_duration_s:SH01",audit([BASE],[dict(BASE,edit_duration_s="5")])["issues"])
    def test_sound_drift(self):self.assertIn("DRIFT_sound_role:SH01",audit([BASE],[dict(BASE,sound_role="MUSIC")])["issues"])
    def test_knowledge_drift(self):self.assertIn("DRIFT_knowledge_mode:SH01",audit([BASE],[dict(BASE,knowledge_mode="AUDIENCE_AHEAD")])["issues"])
    def test_protected_hold_reason(self):self.assertIn("UNJUSTIFIED_PROTECTED_HOLD:SH01",audit([dict(BASE,hold_reason="")],[BASE])["issues"])
    def test_invalid_tension(self):self.assertIn("INVALID_tension_intent:SH01",audit([dict(BASE,tension_intent="LOUD")],[BASE])["issues"])
    def test_artistic_not_verified(self):self.assertEqual(audit([BASE],[BASE])["artistic_quality"],"NOT_VERIFIED")
if __name__=="__main__":unittest.main()
