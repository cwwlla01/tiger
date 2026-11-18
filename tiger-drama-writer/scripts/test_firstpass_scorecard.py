import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from firstpass_scorecard import score
class TestScorecard(unittest.TestCase):
 def test_raw_cannot_be_overwritten_by_revised_result(self):
  with tempfile.TemporaryDirectory() as d:
   raw=Path(d)/'r.md';rev=Path(d)/'v.md'
   raw.write_text('## EP01\n### 场1\n甲：你好',encoding='utf-8')
   rev.write_text(raw.read_text(encoding='utf-8')+'\n甲：继续',encoding='utf-8')
   result=score(raw,rev)
   self.assertEqual(result['raw_structural_pass_count'],0)
   self.assertEqual(result['revision_count'] if 'revision_count' in result else result['rows'][0]['revision_count'],'UNKNOWN')
   self.assertFalse(result['measured_readthrough'])
 def test_text_changes_detected_even_when_structural_stats_same(self):
  with tempfile.TemporaryDirectory() as d:
   raw=Path(d)/'a.md';rev=Path(d)/'b.md'
   raw.write_text('## EP01\n### 场1\n甲：红色',encoding='utf-8')
   rev.write_text('## EP01\n### 场1\n甲：蓝色',encoding='utf-8')
   self.assertTrue(score(raw,rev)['rows'][0]['revision_observed'])
 def test_unchanged_episode_is_not_claimed_revised(self):
  with tempfile.TemporaryDirectory() as d:
   raw=Path(d)/'a.md';rev=Path(d)/'b.md'
   raw.write_text('## EP01\n### 场1\n甲：你好',encoding='utf-8')
   rev.write_bytes(raw.read_bytes())
   self.assertFalse(score(raw,rev)['rows'][0]['revision_observed'])
 def test_mismatched_episode_sets_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   raw=Path(d)/'a.md';rev=Path(d)/'b.md'
   raw.write_text('## EP01\n甲：你好',encoding='utf-8')
   rev.write_text('## EP02\n甲：你好',encoding='utf-8')
   with self.assertRaises(ValueError):score(raw,rev)
 def test_no_invented_revision_count(self):
  with tempfile.TemporaryDirectory() as d:
   raw=Path(d)/'r.md';raw.write_text('## EP01\n甲：你好',encoding='utf-8')
   self.assertEqual(score(raw)['rows'][0]['revision_count'],0)
if __name__=='__main__':unittest.main()
