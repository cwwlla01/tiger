import unittest,tempfile,hashlib
from pathlib import Path
from audit_real_scene_ab_v241 import audit

def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class TestRealSceneAB(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name)
  self.r=[]
  for i in range(2):
   paths={}
   for k in ('source','skill','output','run_log'):
    p=root/f'{i}_{k}.txt';p.write_text(('same source' if k=='source' else f'{i} {k}'),encoding='utf-8');paths[k]=str(p)
   self.r.append(dict(run_id=f'r{i}',scene_id='S1',asset_hash='ASSET',conditions={'seed':42},source_hash=h(paths['source']),skill_hash=h(paths['skill']),output_hash=h(paths['output']),**{k+'_file':v for k,v in paths.items()}))
  self.d={'baseline':self.r[0],'candidate':self.r[1]}
 def test_good_structure(self):self.assertEqual(audit(self.d)['status'],'STRUCTURE_ONLY')
 def test_demo(self):self.assertEqual(audit({'mode':'demo'})['status'],'DEMO_ONLY')
 def test_not_run(self):self.assertEqual(audit({})['status'],'NOT_RUN')
 def test_missing_output(self):self.r[0]['output_file']='missing';self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_tamper_output(self):Path(self.r[0]['output_file']).write_text('changed');self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_same_run_id(self):self.r[1]['run_id']='r0';self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_same_skill(self):self.r[1]['skill_hash']=self.r[0]['skill_hash'];self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_mismatch_assets(self):self.r[1]['asset_hash']='different';self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_mismatch_conditions(self):self.r[1]['conditions']={'seed':0};self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_missing_log(self):self.r[0]['run_log_file']='absent';self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_empty_log(self):Path(self.r[0]['run_log_file']).write_text('');self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
 def test_missing_source(self):self.r[0]['source_file']='absent';self.assertEqual(audit(self.d)['status'],'INCOMPARABLE')
