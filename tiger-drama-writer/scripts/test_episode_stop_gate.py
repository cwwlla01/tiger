import tempfile, unittest
from pathlib import Path
from episode_stop_gate import check

class StopGateTests(unittest.TestCase):
    def test_rejects_thin_episode(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'ep.md';f.write_text('## EP01《薄稿》\n### 1-1 内景·房间·白天\n甲：你好。\n',encoding='utf-8')
            r=check(f,1);self.assertFalse(r['next_episode_allowed_by_static_gate']);self.assertTrue(r['issues'])
    def test_rejects_wrong_episode(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'ep.md';f.write_text('## EP02《错号》\n',encoding='utf-8')
            self.assertIn('WRONG_OR_MULTIPLE_EPISODE_HEADINGS',check(f,1)['issues'])
    def test_rejects_two_episodes(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'ep.md';f.write_text('## EP01《甲》\n## EP02《乙》\n',encoding='utf-8')
            self.assertIn('WRONG_OR_MULTIPLE_EPISODE_HEADINGS',check(f,1)['issues'])
    def test_static_pass_does_not_authorize_editorial(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'ep.md';f.write_text('## EP01《测试》',encoding='utf-8')
            with patch('episode_stop_gate.evaluate', return_value={'files':[{'issues':[]}] }):
                r=check(f,1)
            self.assertTrue(r['next_episode_allowed_by_static_gate'])
            self.assertFalse(r['next_episode_authorized'])
            self.assertTrue(r['editorial_review_required'])
    def test_hash_available(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'ep.md';f.write_text('## EP01《甲》\n',encoding='utf-8')
            self.assertEqual(len(check(f,1)['sha256']),64)

if __name__=='__main__':unittest.main()
