import unittest
from audit_performance_camera_v231 import audit

def rec(**kw):
    r = dict(source_beat_id='B1', performance_trigger='eyes shift', camera_response='HOLD', response_timing='AFTER', attention_target='face', exit_state='still')
    r.update(kw)
    return r

def pair(d=None, v=None):
    return {'director': [rec()] if d is None else d, 'video': [rec()] if v is None else v}

def codes(payload):
    return [issue['code'] for issue in audit(payload)['issues']]

class PerformanceCameraTests(unittest.TestCase):
    def test_clean(self): self.assertEqual(audit(pair())['status'], 'PASS_STRUCTURAL')
    def test_missing_pair(self): self.assertEqual(audit({})['status'], 'NOT_VERIFIED')
    def test_empty_pair(self): self.assertEqual(audit(pair(v=[]))['status'], 'NOT_VERIFIED')
    def test_missing_video_beat(self): self.assertIn('MISSING_VIDEO_BEAT', codes(pair(v=[rec(source_beat_id='B2')])))
    def test_unauthorized_video_beat(self): self.assertIn('UNAUTHORIZED_VIDEO_BEAT', codes(pair(v=[rec(), rec(source_beat_id='B2')])))
    def test_changed_camera(self): self.assertIn('FIELD_DRIFT', codes(pair(v=[rec(camera_response='MOVE')])))
    def test_changed_timing(self): self.assertIn('FIELD_DRIFT', codes(pair(v=[rec(response_timing='BEFORE')])))
    def test_changed_trigger(self): self.assertIn('FIELD_DRIFT', codes(pair(v=[rec(performance_trigger='hand moves')])))
    def test_changed_attention(self): self.assertIn('FIELD_DRIFT', codes(pair(v=[rec(attention_target='door')])))
    def test_invalid_response(self): self.assertIn('INVALID_RESPONSE', codes(pair(d=[rec(camera_response='ZOOM')])))
    def test_invalid_timing(self): self.assertIn('INVALID_TIMING', codes(pair(d=[rec(response_timing='EARLY')])))
    def test_duplicate_beat(self): self.assertIn('DUPLICATE_BEAT', codes(pair(d=[rec(), rec()])))
