import unittest
from audit_reveal_rhythm_v234 import audit

def beat(**kwargs):
    row=dict(source_beat_id='B1',knowledge_mode='AUDIENCE_AHEAD',reveal_event_id='R1',reaction_beat_id='P1',camera_decision='HOLD',cut_trigger='reaction',sound_strategy='ambient',reveal_order=1)
    row.update(kwargs);return row

def check(a=None,b=None):return audit({'director':[beat() if a is None else a],'video':[beat() if b is None else b]})
class TestRevealRhythm(unittest.TestCase):
    def test_pass(self):self.assertEqual(check()['status'],'STRUCTURE_PASS')
    def test_not_artistic_pass(self):self.assertEqual(check()['artistic_quality'],'NOT_VERIFIED')
    def test_mode_drift(self):self.assertIn('HANDOFF_DRIFT',[x['code'] for x in check(b=beat(knowledge_mode='CHARACTER_AHEAD'))['issues']])
    def test_reveal_drift(self):self.assertEqual(check(b=beat(reveal_event_id='R2'))['status'],'FAIL')
    def test_reaction_drift(self):self.assertEqual(check(b=beat(reaction_beat_id='P2'))['status'],'FAIL')
    def test_sound_drift(self):self.assertEqual(check(b=beat(sound_strategy='mute'))['status'],'FAIL')
    def test_cut_drift(self):self.assertEqual(check(b=beat(cut_trigger='door'))['status'],'FAIL')
    def test_order_drift(self):self.assertIn('REVEAL_ORDER_DRIFT',[x['code'] for x in check(b=beat(reveal_order=2))['issues']])
    def test_invalid_mode(self):self.assertIn('INVALID_KNOWLEDGE_MODE',[x['code'] for x in check(a=beat(knowledge_mode='UNKNOWN'))['issues']])
    def test_missing_video(self):self.assertIn('MISSING_VIDEO_BEAT',[x['code'] for x in audit({'director':[beat()],'video':[]})['issues']])
    def test_extra_video(self):self.assertIn('UNSOURCED_VIDEO_BEAT',[x['code'] for x in audit({'director':[],'video':[beat()]})['issues']])
    def test_duplicate(self):self.assertIn('DUPLICATE_ID',[x['code'] for x in audit({'director':[beat(),beat()],'video':[]})['issues']])
    def test_invalid_input(self):self.assertEqual(audit({'director':{},'video':[]})['status'],'INVALID_INPUT')
