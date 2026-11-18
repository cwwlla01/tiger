import unittest
from pathlib import Path
P=Path(__file__).resolve().parent.parent/'fixtures/v256-partial-compilation'
class Partial(unittest.TestCase):
 def test_eight_video_prompts(self):
  s=(P/'05-可继续镜头提示词.md').read_text();self.assertEqual(s.count('```text'),8)
 def test_s07_block(self):
  self.assertIn('BLOCKING_REQUIRES_LAYOUT',(P/'S07-空间布局核验单.md').read_text())
 def test_s09_audio(self):
  self.assertIn('EDIT_AUDIO_ONLY',(P/'05-可继续镜头提示词.md').read_text())
 def test_sound_order(self):
  self.assertIn('先硬切纯黑，再在黑暗中播放第三声',(P/'05-可继续镜头提示词.md').read_text())
 def test_no_false_ready(self):
  self.assertIn('COMPILED_TEXT_ONLY',(P/'README.md').read_text())
if __name__=='__main__':unittest.main()
