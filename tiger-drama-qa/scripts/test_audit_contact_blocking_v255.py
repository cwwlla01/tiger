import unittest
from pathlib import Path
from audit_contact_blocking_v255 import audit

class ContactBlockingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=(Path(__file__).resolve().parents[1]/'fixtures/v255-contact-blocking/S07-走位方案与生产状态.md').read_text(encoding='utf-8')
    def test_unresolved_is_not_accepted(self):self.assertEqual(audit(self.text)['status'],'BLOCKING_REQUIRES_LAYOUT')
    def test_no_global_block(self):self.assertTrue(audit(self.text)['other_shots_not_globally_blocked'])
    def test_missing_evidence_detected(self):self.assertEqual(audit(self.text.replace('PROPOSED','DRAFT'))['status'],'INVALID')
    def test_left_hand_preserved(self):self.assertIn('左手银戒',self.text)
    def test_audio_only(self):self.assertIn('S09=EDIT_AUDIO_ONLY',self.text)
    def test_layout_required(self):self.assertIn('平面图',self.text)
