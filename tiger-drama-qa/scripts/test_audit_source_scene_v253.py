import unittest,tempfile,shutil,json
from pathlib import Path
from audit_source_scene_v253 import audit
BASE=Path(__file__).resolve().parent.parent/'fixtures/v253-real-source'
class TestSceneV253(unittest.TestCase):
 def test_pass(self):
  self.assertEqual(audit(BASE)['status'],'TEST_SCRIPT_STRUCTURE_ONLY')
 def test_nine(self):
  self.assertEqual(audit(BASE)['shots'],9)
 def test_no_blind_claim(self):
  self.assertFalse(json.loads((BASE/'manifest.json').read_text())['independent_blind_run'])
 def test_source_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   for p in BASE.iterdir():shutil.copy2(p,d)
   with (Path(d)/'01-原始测试剧本.md').open('a') as f:f.write('tamper')
   self.assertIn('source_sha256_MISMATCH',audit(d)['errors'])
 def test_storyboard_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   for p in BASE.iterdir():shutil.copy2(p,d)
   with (Path(d)/'03-专业导演分镜.md').open('a') as f:f.write('tamper')
   self.assertIn('storyboard_sha256_MISMATCH',audit(d)['errors'])
