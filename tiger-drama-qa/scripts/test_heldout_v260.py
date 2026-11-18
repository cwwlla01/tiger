import json,unittest
from pathlib import Path
P=Path(__file__).parent/'fixtures/heldout_v260'
class HeldoutV260(unittest.TestCase):
 def test_source(self):
  x=json.loads((P/'source.json').read_text(encoding='utf-8'));self.assertEqual(len(x['canon_events']),4);self.assertEqual(x['duration_seconds'],15)
 def test_two_distinct_plans(self):
  a=(P/'A_CONVENTIONAL.md').read_text(encoding='utf-8');b=(P/'B_SELECTED_03.md').read_text(encoding='utf-8');self.assertIn('正面中景',a);self.assertIn('侧后方中景',b);self.assertNotEqual(a,b)
 def test_duration(self):
  s=(P/'B_SELECTED_03.md').read_text(encoding='utf-8');self.assertIn('3+3+5+4=15秒',s)
 def test_physical_obstruction(self):
  s=(P/'B_SELECTED_03.md').read_text(encoding='utf-8');self.assertIn('完全遮挡红伞',s);self.assertIn('同一柱间位置空无红伞',s)
 def test_unknowns_preserved(self):
  s=(P/'B_SELECTED_03.md').read_text(encoding='utf-8');self.assertIn('不增加伞下人物、灵异原因',s)
 def test_evidence_boundary(self):
  s=(P/'COMPARISON.md').read_text(encoding='utf-8');self.assertIn('独立盲测NOT_VERIFIED',s);self.assertIn('成片质量NOT_VERIFIED',s)
if __name__=='__main__':unittest.main()
