import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from runtime_proxy import estimate

class RuntimeProxyTest(unittest.TestCase):
 def test_range_and_no_measured_claim(self):
  with tempfile.TemporaryDirectory() as td:
   f=Path(td)/'a.md'
   f.write_text('## EP01｜测试\n### SC01｜房间\n甲：我现在必须选择是否告诉你这件事。\n乙：你确定吗？我不会帮你隐瞒。\n### SC02｜门口\n△关门。\n',encoding='utf-8')
   r=estimate(f)
   e=r['episodes'][0]
   self.assertEqual(e['scenes'],2)
   self.assertIsNone(e['measured_runtime_seconds'])
   self.assertLessEqual(*e['estimated_seconds_range'])
 def test_bad_assumptions_rejected(self):
  with self.assertRaises(ValueError):estimate('unused',300,180)
  with self.assertRaises(ValueError):estimate('unused',180,300,(10,-1))
if __name__=='__main__':unittest.main()
