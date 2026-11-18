import importlib.util, unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts'/'audit_mechanism_diversity.py'
s=importlib.util.spec_from_file_location('audit_mechanism_diversity',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class AuditTest(unittest.TestCase):
 def test_ungrounded(self):
  txt='## EP01\n主角争吵。';led={'episodes':[{'episode':'EP01','mechanism':'confrontation','decisive_action':'不存在','cost':'主角争吵。','state_change':'主角争吵。'}]}
  self.assertFalse(m.inspect(txt,led)['ok'])
 def test_three_repeats(self):
  txt=''.join(f'## EP0{i}\n行动{i}\n' for i in range(1,4))
  led={'episodes':[{'episode':f'EP0{i}','mechanism':'paperwork','decisive_action':f'行动{i}','cost':f'行动{i}','state_change':f'行动{i}'} for i in range(1,4)]}
  self.assertFalse(m.inspect(txt,led)['ok'])
 def test_diverse(self):
  txt=''.join(f'## EP0{i}\n行动{i}\n' for i in range(1,4))
  led={'episodes':[{'episode':f'EP0{i}','mechanism':str(i),'decisive_action':f'行动{i}','cost':f'行动{i}','state_change':f'行动{i}'} for i in range(1,4)]}
  self.assertTrue(m.inspect(txt,led)['ok'])
if __name__=='__main__':unittest.main()
