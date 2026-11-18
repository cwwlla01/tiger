import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
D=ROOT/'director/tiger-drama-director';V=ROOT/'video/tiger-video-prompt';Q=ROOT/'qa/tiger-drama-qa'
class Integration(unittest.TestCase):
 def test_director_reference(self):
  s=(D/'references/jinguang-camera-integration-v251.md').read_text();self.assertIn('固定机位',s);self.assertIn('信息边界',s)
 def test_director_entrypoint(self):self.assertIn('jinguang-camera-integration-v251.md',(D/'SKILL.md').read_text())
 def test_video_entrypoint(self):self.assertIn('jinguang-camera-compilation-v251.md',(V/'SKILL.md').read_text())
 def test_qa_entrypoint(self):self.assertIn('jinguang-camera-qa-v251.md',(Q/'SKILL.md').read_text())
 def test_no_forced_first_frame(self):self.assertIn('首帧不强制',(V/'references/jinguang-camera-compilation-v251.md').read_text())
 def test_no_unverified_art_claim(self):self.assertIn('没有真实视频证据',(Q/'references/jinguang-camera-qa-v251.md').read_text())
 def test_preserve_prior_jinguang_reference(self):self.assertIn('金光',(D/'references/tactical-narrative-staging.md').read_text())
if __name__=='__main__':unittest.main()
