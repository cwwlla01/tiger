import unittest,tempfile,hashlib
from pathlib import Path
from audit_historical_runs_v243 import audit

def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class HistoricalABTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();p=Path(self.tmp.name)
  self.r=[]
  for i,v in enumerate(('2.38','2.39')):
   s=p/f'skill{i}.zip';s.write_bytes(f'skill {i}'.encode())
   src=p/'source.txt';src.write_text('same script',encoding='utf-8')
   out=p/f'out{i}.md';out.write_text(f'output {i}',encoding='utf-8')
   log=p/f'log{i}.txt';log.write_text(f'independent run {i}',encoding='utf-8')
   self.r.append(dict(run_id=f'run{i}',version=v,skill_zip=str(s),skill_sha256=h(s),source_file=str(src),source_sha256=h(src),assets_sha256='assets',settings={'seed':1},run_log=str(log),output_file=str(out),output_sha256=h(out),provenance_verified=True))
 def tearDown(self):self.tmp.cleanup()
 def data(self):return {'runs':self.r}
 def test_valid_structure(self):self.assertEqual(audit(self.data())['status'],'STRUCTURE_ONLY')
 def test_demo(self):self.assertEqual(audit({'evidence_type':'DEMO_ONLY','runs':self.r})['status'],'DEMO_ONLY')
 def test_missing_runs(self):self.assertEqual(audit({'runs':[]})['status'],'NOT_RUN')
 def test_missing_file(self):self.r[0]['output_file']='/missing';self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_modified_output(self):Path(self.r[0]['output_file']).write_text('changed');self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_mismatched_source(self):self.r[0]['source_sha256']='bad';self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_mismatched_assets(self):self.r[0]['assets_sha256']='other';self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_mismatched_settings(self):self.r[0]['settings']={'seed':2};self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_same_run_id(self):self.r[1]['run_id']='run0';self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_wrong_version(self):self.r[1]['version']='2.42';self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_empty_log(self):Path(self.r[1]['run_log']).write_text('');self.assertEqual(audit(self.data())['status'],'INCOMPARABLE')
 def test_unverified_provenance(self):self.r[1]['provenance_verified']=False;self.assertEqual(audit(self.data())['status'],'UNVERIFIED_PROVENANCE')
