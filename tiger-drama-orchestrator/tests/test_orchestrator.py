import importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('orch',Path(__file__).resolve().parents[1]/'scripts'/'orchestrator.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Tests(unittest.TestCase):
 def test_empty(self):
  with tempfile.TemporaryDirectory() as d:
   state=mod.scan(d);self.assertEqual(state['stages']['01']['status'],'NOT_STARTED');self.assertFalse(mod.plan(state)['tasks'][1]['ready_for_authoritative_handoff'])
 def test_existing_is_not_approved(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'03-专业导演分镜.md').write_text('candidate')
   state=mod.scan(d);self.assertEqual(state['stages']['03']['status'],'NOT_VERIFIED');self.assertEqual(len(state['stages']['03']['artifacts'][0]['sha256']),64)
 def test_approved_only_if_explicit(self):
  with tempfile.TemporaryDirectory() as d:
   state=mod.scan(d);state['stages']['01']['status']='APPROVED'
   tasks=mod.plan(state)['tasks'];self.assertTrue(next(t for t in tasks if t['stage']=='02')['ready_for_authoritative_handoff'])
 def test_director_uses_asset_look_context_before_candidate_handoff(self):
  with tempfile.TemporaryDirectory() as d:
   state=mod.scan(d)
   state['stages']['01']['status']='APPROVED'
   state['stages']['02']['status']='CANDIDATE'
   task=next(t for t in mod.plan(state)['tasks'] if t['stage']=='03')
   self.assertTrue(task['ready_for_candidate'])
   self.assertFalse(task['ready_for_authoritative_handoff'])
 def test_candidate_chain_does_not_claim_authoritative_handoff(self):
  with tempfile.TemporaryDirectory() as d:
   state=mod.scan(d)
   for stage in ('01','02','03','04'):
    state['stages'][stage]['status']='CANDIDATE'
   task=next(t for t in mod.plan(state)['tasks'] if t['stage']=='05')
   self.assertTrue(task['ready_for_candidate'])
   self.assertFalse(task['ready_for_authoritative_handoff'])
if __name__=='__main__':unittest.main()
