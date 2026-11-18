import tempfile, unittest
from pathlib import Path
from trace_repair_impact import trace,sha
class TraceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.cand=self.root/'candidates';self.cand.mkdir()
  (self.root/'02.md').write_text('A old B',encoding='utf-8');(self.cand/'02.md').write_text('A new B',encoding='utf-8')
  (self.root/'03-专业导演分镜.md').write_text('SCENE-006 rail intact\n',encoding='utf-8')
  for n in ['04-画面帧生成提示词.md','05-视频生成提示词.md']:(self.root/n).write_text('SCENE-006',encoding='utf-8')
  self.ticket={'tickets':[{'id':'P0-SCENE-006','file':'02.md','old':'old','new':'new','source_sha256':sha(self.root/'02.md'),'source_evidence':'03-专业导演分镜.md 第1行'}]}
 def tearDown(self):self.tmp.cleanup()
 def test_valid(self):
  x=trace(self.root,self.ticket,self.cand)['tickets'][0];self.assertEqual(x['flags'],[]);self.assertEqual(len(x['downstream']),3)
 def test_tamper(self):
  (self.cand/'02.md').write_text('wrong',encoding='utf-8');x=trace(self.root,self.ticket,self.cand)['tickets'][0];self.assertIn('CANDIDATE_EXACT_CHANGE_FAILED',x['flags'])
 def test_missing_evidence(self):
  self.ticket['tickets'][0]['source_evidence']='unknown';x=trace(self.root,self.ticket,self.cand)['tickets'][0];self.assertIn('NO_VERIFIABLE_LINE_EVIDENCE',x['flags'])
if __name__=='__main__':unittest.main()
