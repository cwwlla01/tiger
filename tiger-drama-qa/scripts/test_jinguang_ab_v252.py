import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_jinguang_ab_v252 import audit,BASE
class Benchmark(unittest.TestCase):
 def test_status(self):self.assertEqual(audit()['status'],'MANUAL_ILLUSTRATIVE_COMPARISON')
 def test_two_plans(self):self.assertEqual(len(audit()['plans']),2)
 def test_beats(self):
  for p in audit()['plans'].values():self.assertEqual(p['beats'],['B1','B2','B3','B4'])
 def test_no_independent_claim(self):self.assertFalse(audit()['independent_runs'])
 def test_no_visual_claim(self):self.assertFalse(audit()['visual_evidence'])
 def test_different_pacing(self):self.assertEqual(sorted(p['seconds'] for p in audit()['plans'].values()),[14,16])
 def test_comparison(self):self.assertIn('节奏代价',(BASE/'COMPARISON.md').read_text())
 def test_director_entry(self):self.assertIn('jinguang-applied-benchmark-v252.md',(Path(__file__).resolve().parents[3]/'director/tiger-drama-director/SKILL.md').read_text())
 def test_video_entry(self):self.assertIn('jinguang-benchmark-handoff-v252.md',(Path(__file__).resolve().parents[3]/'video/tiger-video-prompt/SKILL.md').read_text())
 def test_qa_entry(self):self.assertIn('jinguang-benchmark-review-v252.md',(Path(__file__).resolve().parents[3]/'qa/tiger-drama-qa/SKILL.md').read_text())
if __name__=='__main__':unittest.main()
