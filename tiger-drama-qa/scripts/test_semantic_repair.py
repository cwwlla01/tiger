import unittest,tempfile,json,hashlib
from pathlib import Path
from semantic_repair import run
class TestSemantic(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.p=self.root/'02-example.md';self.p.write_text('initial platform includes later damage\n',encoding='utf-8')
 def ticket(self,**kw):
  t={'id':'P0-01','file':self.p.name,'source_sha256':hashlib.sha256(self.p.read_bytes()).hexdigest(),'old':'includes later damage','new':'intact before impact','source_evidence':'03 storyboard event T-023','rationale':'stage pollution','owner':'asset producer'};t.update(kw);f=self.root/'tickets.json';f.write_text(json.dumps([t]));return f
 def test_proposal_no_source_edit(self):
  r=run(self.root,self.ticket(),self.root/'out');self.assertEqual(r['tickets'][0]['status'],'PROPOSED');self.assertIn('later damage',self.p.read_text())
 def test_candidate_copy_only(self):
  r=run(self.root,self.ticket(),self.root/'out',True);self.assertIn('intact before impact',(self.root/'out/candidates/02-example.md').read_text());self.assertIn('later damage',self.p.read_text());self.assertEqual(r['acceptance'],'NOT_VERIFIED')
 def test_stale_hash_blocked(self):self.assertEqual(run(self.root,self.ticket(source_sha256='bad'),self.root/'out')['tickets'][0]['status'],'BLOCKED')
 def test_ambiguous_quote_blocked(self):self.assertEqual(run(self.root,self.ticket(old='a'),self.root/'out')['tickets'][0]['status'],'BLOCKED')
 def test_authoritative_03_blocked(self):self.assertEqual(run(self.root,self.ticket(file='03-专业导演分镜.md'),self.root/'out')['tickets'][0]['status'],'BLOCKED')
 def test_no_evidence_blocked(self):self.assertEqual(run(self.root,self.ticket(source_evidence=''),self.root/'out')['tickets'][0]['status'],'BLOCKED')
if __name__=='__main__':unittest.main()
