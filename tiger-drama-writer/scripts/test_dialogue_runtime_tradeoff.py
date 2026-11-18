import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dialogue_runtime_tradeoff import analyze


class TradeoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'EP01.md'
        self.path.write_text('## EP01｜测试\n### SC01｜家中｜夜｜内\n△一声巨响。\n阿甲：我不去。\n阿乙：为什么？\n',encoding='utf-8')
    def tearDown(self): self.tmp.cleanup()
    def test_deficit_and_runtime_penalty(self):
        x=analyze(self.path)
        self.assertEqual(x['dialogue_turns'],2)
        self.assertEqual(x['chars_to_clear_average_heuristic'],22)
        self.assertEqual(x['duration_penalty_if_only_adding_chars_seconds'],[4.4,7.3])
        self.assertEqual(x['source_sha256'],hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertFalse(x['actual_rehearsal_measured'])
    def test_no_shortfall(self):
        self.path.write_text('## EP01｜测试\n### SC01｜家中｜夜｜内\n△关门。\n阿甲：这件事情我们必须先想清楚再做决定。\n',encoding='utf-8')
        self.assertEqual(analyze(self.path)['chars_to_clear_average_heuristic'],0)
    def test_reject_bad_target(self):
        with self.assertRaises(ValueError):analyze(self.path,0)
    def test_refuse_multi_episode(self):
        with self.path.open('a',encoding='utf-8') as f:f.write('\n## EP02｜续\n### SC01｜家中｜夜｜内\n阿甲：还没完。\n')
        with self.assertRaises(ValueError):analyze(self.path)

if __name__=='__main__':unittest.main()
