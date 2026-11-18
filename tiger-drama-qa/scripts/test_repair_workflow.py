import tempfile,unittest,json
from pathlib import Path
from repair_workflow import fix_format,run
class TestQA(unittest.TestCase):
 def test_format_idempotent(self):
  x='hello  \n\n\n\nworld\t\n';self.assertEqual(fix_format(fix_format(x)),fix_format(x))
 def test_dry_run_unchanged(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'02-test.md').write_text('a  \n\n\n\n b\n');before=(p/'02-test.md').read_bytes()
   r=run(p,p/'out');self.assertEqual(before,(p/'02-test.md').read_bytes());self.assertEqual(r['mode'],'DRY_RUN');self.assertEqual(len(r['proposed_format_repairs']),1)
 def test_apply_copy_only(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'05-test.md').write_text('a  \n');r=run(p,p/'out',True)
   self.assertEqual((p/'05-test.md').read_text(),'a  \n');self.assertEqual((p/'out/repaired/05-test.md').read_text(),'a\n');self.assertEqual(r['acceptance'],'NOT_VERIFIED')
 def test_no_semantic_autofix(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);r=run(p,p/'out',True)
   self.assertEqual(r['semantic_auto_fixes'],0);self.assertTrue(any(f['code']=='INPUT_MISSING' and f['fix_mode']=='MANUAL' for f in r['findings']))
if __name__=='__main__':unittest.main()
