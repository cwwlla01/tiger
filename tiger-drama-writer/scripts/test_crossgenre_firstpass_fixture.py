"""Portable authored first-pass pressure fixture: community family comedy.

Static checks, runtime-proxy checks, and content quality remain separate.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from firstpass_dual_gate import assess
from audit_script_batch import audit

FIXTURES = HERE.parent / 'tests' / 'fixtures' / 'community_comedy'


class CrossGenreFirstpassFixture(unittest.TestCase):
    def test_three_authored_episodes_present(self):
        for ep in range(1, 4):
            self.assertTrue((FIXTURES / f'EP{ep:02d}_raw.md').is_file())

    def test_three_episode_structural_first_pass(self):
        for ep in range(1, 4):
            with self.subTest(episode=ep):
                outcome = assess(str(FIXTURES / f'EP{ep:02d}_raw.md'), ep)
                self.assertTrue(outcome['static_pass'], outcome['issues'])
                self.assertEqual(outcome['runtime_proxy_status'], 'UPPER_EXCEEDS_TARGET')
                self.assertTrue(outcome['requires_beat_plan_or_rehearsal'])
                self.assertFalse(outcome['next_episode_authorized'])

    def test_prose_is_not_spoofed_as_multi_episode(self):
        for ep in range(1, 4):
            with self.subTest(episode=ep):
                report = audit(str(FIXTURES / f'EP{ep:02d}_raw.md'))
                self.assertEqual([row['episode'] for row in report['episodes']], [ep])
                self.assertEqual(report['episodes'][0]['scenes'], 3)

    def test_fixture_has_sequential_distinct_script_bytes(self):
        import hashlib
        hashes = [hashlib.sha256((FIXTURES / f'EP{ep:02d}_raw.md').read_bytes()).hexdigest() for ep in range(1, 4)]
        self.assertEqual(len(set(hashes)), 3)


if __name__ == '__main__':
    unittest.main()
