"""A real genre-different firstpass overrun and constrained rewrite regression."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from firstpass_dual_gate import assess

class ComedyRevisionTests(unittest.TestCase):
    def test_original_is_genuinely_over_minimum(self):
        p = ROOT/'tests/fixtures/community_comedy/EP04_raw.md'
        result = assess(str(p), 4)
        self.assertTrue(result['static_pass'], result['issues'])
        self.assertEqual(result['runtime_proxy_status'], 'MINIMUM_EXCEEDS_TARGET')
        self.assertTrue(result['needs_rewrite_before_next_episode'])
    def test_revision_keeps_structure_and_reduces_proxy(self):
        p = ROOT/'tests/fixtures/community_comedy/EP04_revision1.md'
        result = assess(str(p), 4)
        self.assertTrue(result['static_pass'], result['issues'])
        self.assertEqual(result['runtime_proxy_status'], 'UPPER_EXCEEDS_TARGET')
        self.assertEqual(result['runtime_proxy']['scenes'], 3)
        self.assertGreaterEqual(result['runtime_proxy']['dialogue_turns'], 24)
        self.assertFalse(result['needs_rewrite_before_next_episode'])
        self.assertFalse(result['next_episode_authorized'])
    def test_revision_is_not_original(self):
        a = ROOT/'tests/fixtures/community_comedy/EP04_raw.md'
        b = ROOT/'tests/fixtures/community_comedy/EP04_revision1.md'
        self.assertNotEqual(a.read_bytes(), b.read_bytes())

if __name__ == '__main__': unittest.main()
