import unittest, tempfile, shutil, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_compiled_scene_v248 import audit
FX=Path(__file__).parent/'fixtures/working_scene_v248'
class TestCompiled(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for f in FX.iterdir():shutil.copy2(f,self.root/f.name)
 def tearDown(self):self.tmp.cleanup()
 def mutate(self,fn):
  p=self.root/'manifest.json';d=json.loads(p.read_text());fn(d);p.write_text(json.dumps(d,ensure_ascii=False))
 def test_clean(self):self.assertEqual(audit(self.root)['status'],'STRUCTURE_ONLY')
 def test_order(self):self.mutate(lambda d:d['shots'][0].update(shot_id='S99'));self.assertIn('SHOT_ORDER',audit(self.root)['errors'])
 def test_beat(self):self.mutate(lambda d:d['shots'][0].update(source_beat_id='B9'));self.assertIn('BEAT_COVERAGE',audit(self.root)['errors'])
 def test_duration(self):self.mutate(lambda d:d['shots'][0].update(duration_estimate_s=8));self.assertIn('DURATION',audit(self.root)['errors'])
 def test_s03_turn(self):self.mutate(lambda d:d['shots'][2].update(action='旋转门把'));self.assertIn('S03_CONTINUITY',audit(self.root)['errors'])
 def test_s03_end(self):self.mutate(lambda d:d['shots'][2].update(end_state='手已松开'));self.assertIn('S03_CONTINUITY',audit(self.root)['errors'])
 def test_s04_sound(self):self.mutate(lambda d:d['shots'][3].update(audio='阿禾松手后声音停止'));self.assertIn('S04_SOUND_ORDER',audit(self.root)['errors'] if '先' not in '阿禾松手后声音停止' else [] )
 def test_s04_frame(self):self.mutate(lambda d:d['shots'][3].update(first_frame='手已松开'));self.assertIn('PREMATURE_RELEASE',audit(self.root)['errors'])
 def test_file_hash(self):(self.root/'05-视频生成提示词.md').write_text('changed');self.assertTrue(any(x.startswith('FILE_HASH') for x in audit(self.root)['errors']))
 def test_missing_file(self):(self.root/'04-画面帧生成提示词.md').unlink();self.assertTrue(any(x.startswith('FILE_HASH') for x in audit(self.root)['errors']))
 def test_missing_manifest_entry(self):self.mutate(lambda d:d['files'].pop('04-画面帧生成提示词.md'));self.assertTrue(any(x.startswith('MISSING') for x in audit(self.root)['errors']))
 def test_door(self):self.mutate(lambda d:d['shots'][0].update(first_frame='走廊',end_state='走廊'));self.assertIn('DOOR_STATE:S01',audit(self.root)['errors'])
