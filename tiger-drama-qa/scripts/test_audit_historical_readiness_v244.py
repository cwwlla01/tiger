import unittest,tempfile,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_historical_readiness_v244 import inspect
class ReadinessTests(unittest.TestCase):
 def make(self,path,skill,extra=None):
  with zipfile.ZipFile(path,'w') as z:
   z.writestr('tiger-drama-director/SKILL.md',skill)
   if extra:z.writestr(extra,'data')
 def test_status(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'old');self.make(b,'new')
   self.assertEqual(inspect(a,b)['status'],'SOURCE_DIFF_ONLY')
 def test_no_fake_run(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'old');self.make(b,'new')
   self.assertFalse(inspect(a,b)['historical_runs_executed'])
 def test_no_blind_claim(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'old');self.make(b,'new')
   self.assertFalse(inspect(a,b)['blind_review_performed'])
 def test_changed_entry(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'old');self.make(b,'new')
   self.assertIn('tiger-drama-director/SKILL.md',inspect(a,b)['files_changed'])
 def test_added_file(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'same');self.make(b,'same','x.md')
   self.assertIn('x.md',inspect(a,b)['files_added'])
 def test_removed_file(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'same','x.md');self.make(b,'same')
   self.assertIn('x.md',inspect(a,b)['files_removed'])
 def test_identical(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip';self.make(a,'same');self.make(b,'same')
   self.assertEqual(inspect(a,b)['files_changed'],[])
 def test_missing_skill(self):
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'a.zip';b=Path(t)/'b.zip'
   with zipfile.ZipFile(a,'w') as z:z.writestr('other','x')
   self.make(b,'ok')
   with self.assertRaises(ValueError):inspect(a,b)
if __name__=='__main__':unittest.main()
