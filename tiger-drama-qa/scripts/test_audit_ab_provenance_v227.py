import unittest, tempfile, hashlib
from pathlib import Path
from audit_ab_provenance_v227 import audit,sha

class TestABProvenance(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup); self.root=Path(self.t.name)
  source=self.root/'source';source.write_text('source')
  self.m={'source_path':str(source),'source_sha256':sha(source)}
  for side in ('baseline','candidate'):
   log=self.root/(side+'.log');log.write_text('run')
   rec={'run_id':side,'skill_sha256':'a'*64,'execution_log':str(log),'artifacts':{}}
   for stage in ('03','04','05'):
    p=self.root/(side+stage);p.write_text(side+stage)
    rec['artifacts'][stage]={'path':str(p),'sha256':sha(p)}
   self.m[side]=rec
 def test_valid_pair(self):self.assertEqual(audit(self.m)['status'],'PAIRED_PROVENANCE_READY')
 def test_missing_candidate(self):
  del self.m['candidate'];self.assertIn('candidate_provenance_incomplete',audit(self.m)['problems'])
 def test_source_tamper(self):
  Path(self.m['source_path']).write_text('changed');self.assertIn('source_hash_mismatch',audit(self.m)['problems'])
 def test_artifact_tamper(self):
  Path(self.m['candidate']['artifacts']['03']['path']).write_text('changed');self.assertIn('candidate_03_hash_mismatch',audit(self.m)['problems'])
 def test_missing_log(self):
  Path(self.m['candidate']['execution_log']).unlink();self.assertIn('candidate_execution_log_missing',audit(self.m)['problems'])
 def test_shared_run(self):
  self.m['candidate']['run_id']='baseline';self.assertIn('shared_run_id',audit(self.m)['problems'])
 def test_identical_artifact(self):
  item=self.m['candidate']['artifacts']['05'];src=self.m['baseline']['artifacts']['05']['path'];item['path']=src;item['sha256']=sha(src)
  self.assertIn('identical_artifact_05',audit(self.m)['problems'])
 def test_missing_stage(self):
  del self.m['baseline']['artifacts']['04'];self.assertIn('baseline_04_missing',audit(self.m)['problems'])
 def test_no_quality_claim(self):self.assertFalse(audit(self.m)['quality_improvement_verified'])
