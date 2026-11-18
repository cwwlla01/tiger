import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from audit_working_scene_v246 import audit
ROOT=Path(__file__).parent/'fixtures'/'working_scene_v246'
class WorkingSceneTests(unittest.TestCase):
 def test_fixture(self):self.assertEqual(audit(ROOT)['status'],'EXPLORATORY_ONLY')
 def test_counts(self):self.assertEqual(audit(ROOT)['shots'],4)
 def test_duration(self):self.assertEqual(audit(ROOT)['duration_s'],16)
 def mutate(self,func):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   for name in ('manifest.json','source.json','03-working-draft.md'):(p/name).write_bytes((ROOT/name).read_bytes())
   m=json.loads((p/'manifest.json').read_text());func(m,p)
   (p/'manifest.json').write_text(json.dumps(m));return audit(p)['status']
 def test_false_historical(self):self.assertEqual(self.mutate(lambda m,p:m.update(historical_independent_runs=True)),'INVALID')
 def test_duplicate_shot(self):self.assertEqual(self.mutate(lambda m,p:m['shots'][1].update(shot_id='S01')),'INVALID')
 def test_missing_beat(self):self.assertEqual(self.mutate(lambda m,p:m['shots'][1].update(beat_ids=[])),'INVALID')
 def test_extra_beat(self):self.assertEqual(self.mutate(lambda m,p:m['shots'][1].update(beat_ids=['B2','B9'])),'INVALID')
 def test_bad_duration(self):self.assertEqual(self.mutate(lambda m,p:m['shots'][1].update(duration_s=0)),'INVALID')
 def test_hash_tamper(self):self.assertEqual(self.mutate(lambda m,p:(p/'03-working-draft.md').write_text('tampered')),'INVALID')
