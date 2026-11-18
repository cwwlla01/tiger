import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'qa'))
from audit_threat_chain_v218 import audit,FIELDS

def make():
 t={'take_id':'T-001',**{k:'fixed' for k in FIELDS}}
 return {'stages':{k:{'takes':[t.copy()]} for k in ('03','04','05')}}
class Tests(unittest.TestCase):
 def test_pass(self):self.assertEqual(audit(make()),[])
 def test_missing_take(self):
  d=make();d['stages']['04']['takes']=[];self.assertTrue(any('missing take' in x for x in audit(d)))
 def test_extra_take(self):
  d=make();d['stages']['05']['takes'].append({'take_id':'T-999'});self.assertTrue(any('extra take' in x for x in audit(d)))
 def test_duplicate(self):
  d=make();d['stages']['03']['takes'].append(d['stages']['03']['takes'][0].copy());self.assertTrue(any('duplicate' in x for x in audit(d)))
 def test_missing_field(self):
  d=make();del d['stages']['03']['takes'][0]['cause'];self.assertTrue(any('missing cause' in x for x in audit(d)))
