import unittest,tempfile,shutil,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_working_scene_review_v247 import audit
FIX=Path(__file__).parent/'fixtures/working_scene_v247'
class TestReview(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); shutil.copytree(FIX,self.root/'scene'); self.scene=self.root/'scene'
 def tearDown(self):self.tmp.cleanup()
 def edit(self,fn):
  p=self.scene/'manifest.json'; m=json.loads(p.read_text());fn(m);p.write_text(json.dumps(m))
 def test_valid(self):self.assertEqual(audit(self.scene)['status'],'WORKING_DRAFT_REVIEWED')
 def test_duration(self):self.assertEqual(audit(self.scene)['duration_s'],16)
 def test_not_historical(self):self.assertFalse(audit(self.scene)['historical_ab'])
 def test_missing_file(self):(self.scene/'source.json').unlink();self.assertEqual(audit(self.scene)['status'],'INVALID')
 def test_hash(self):(self.scene/'03-revised-draft.md').write_text('tampered');self.assertEqual(audit(self.scene)['reason'],'hash mismatch')
 def test_false_history(self):self.edit(lambda m:m.update(historical_independent_runs=True));self.assertEqual(audit(self.scene)['reason'],'provenance')
 def test_beat_loss(self):self.edit(lambda m:m['shots'][0].update(beat_ids=[]));self.assertEqual(audit(self.scene)['status'],'INVALID')
 def test_duplicate(self):self.edit(lambda m:m['shots'][1].update(shot_id='S01'));self.assertEqual(audit(self.scene)['status'],'INVALID')
 def test_axis(self):self.edit(lambda m:m['shots'][1].update(axis='reverse'));self.assertEqual(audit(self.scene)['reason'],'axis')
 def test_audio_order(self):self.edit(lambda m:m['shots'][3].update(action='release'));self.assertEqual(audit(self.scene)['reason'],'action causal chain')
 def test_review_trace(self):self.edit(lambda m:m.update(review_findings=[]));self.assertEqual(audit(self.scene)['reason'],'review trace')
 def test_negative_duration(self):self.edit(lambda m:m['shots'][0].update(duration_s=-1));self.assertEqual(audit(self.scene)['reason'],'duration')
