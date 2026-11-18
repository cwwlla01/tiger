import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'fixtures/v254-scene-review'
class TestV254Review(unittest.TestCase):
 def test_review(self):
  s=(P/'DIRECTOR_REVIEW.md').read_text(); self.assertIn('BLOCKING_REQUIRES_LAYOUT',s); self.assertIn('EDIT_AUDIO_ONLY',s)
 def test_source_coverage(self):
  s=(P/'03-导演复审工作稿.md').read_text()
  for i in range(1,10): self.assertIn(f'源事件 {i:02}',s)
 def test_shot_split(self):
  s=(P/'03-导演复审工作稿.md').read_text();self.assertIn('S01A 4秒',s);self.assertIn('S01B 2秒',s)
 def test_sound_after_black(self):
  s=(P/'03-导演复审工作稿.md').read_text();self.assertIn('硬切纯黑后再触发第三声',s)
 def test_geometry_not_faked(self):
  s=(P/'03-导演复审工作稿.md').read_text();self.assertIn('不允许凭空瞬移',s)
 def test_no_forced_video(self):
  s=(P/'03-导演复审工作稿.md').read_text();self.assertIn('不要求生成 AI 视频',s)
