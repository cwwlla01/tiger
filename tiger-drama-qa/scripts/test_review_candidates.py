import json, tempfile, unittest
from pathlib import Path
from semantic_repair import run
from review_candidates import review
from hashlib import sha256

class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'root';self.root.mkdir();self.out=Path(self.tmp.name)/'out'
        self.p=self.root/'02-example.md';self.p.write_text('old\n',encoding='utf-8')
        ticket={'tickets':[{'id':'P0-1','file':self.p.name,'source_sha256':sha256(self.p.read_bytes()).hexdigest(),'old':'old','new':'new','source_evidence':'03 scene source','rationale':'test','owner':'asset producer'}]}
        self.ticket=Path(self.tmp.name)/'ticket.json';self.ticket.write_text(json.dumps(ticket))
        run(self.root,self.ticket,self.out,True)
    def tearDown(self):self.tmp.cleanup()
    def check(self):return review(self.root,self.out/'semantic-repair-report.json',self.out/'independent.json')['tickets'][0]
    def test_valid_candidate_requires_semantic_review(self):
        self.assertEqual(self.check()['status'],'READY_FOR_INDEPENDENT_SEMANTIC_REVIEW')
        self.assertEqual(json.loads((self.out/'independent.json').read_text())['closed_tickets'],0)
    def test_tampered_candidate_blocked(self):
        (self.out/'candidates'/self.p.name).write_text('tampered')
        self.assertEqual(self.check()['status'],'BLOCKED')
    def test_changed_source_blocked(self):
        self.p.write_text('changed')
        self.assertEqual(self.check()['status'],'BLOCKED')
    def test_missing_candidate_blocked(self):
        (self.out/'candidates'/self.p.name).unlink()
        self.assertEqual(self.check()['status'],'BLOCKED')
if __name__=='__main__':unittest.main()
