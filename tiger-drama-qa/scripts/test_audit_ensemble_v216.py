import unittest,copy
from audit_ensemble_v216 import audit
B={"beat_id":"B01","present_characters":["A","B","C"],"attention_anchor":"A","active_speaker":"B","information_holders":["A"],"reaction_targets":["C"],"blocking_state":"A-left B-center C-right","screen_axis":"east-west","reveal_order":["sound","look","door"]}
def fixture():return {"stages":{s:{"beats":[copy.deepcopy(B)]} for s in ("03","04","05")}}
class TestEnsemble(unittest.TestCase):
 def test_clean(self):self.assertEqual(audit(fixture()),[])
 def test_missing_stage(self):
  x=fixture();del x['stages']['05'];self.assertIn('NOT_VERIFIED',str(audit(x)))
 def test_duplicate(self):
  x=fixture();x['stages']['03']['beats'].append(copy.deepcopy(B));self.assertIn('duplicate',str(audit(x)))
 def test_missing_beat(self):
  x=fixture();x['stages']['04']['beats']=[];self.assertIn('missing beat',str(audit(x)))
 def test_extra_beat(self):
  x=fixture();y=copy.deepcopy(B);y['beat_id']='B02';x['stages']['05']['beats'].append(y);self.assertIn('extra beat',str(audit(x)))
 def test_speaker_absent(self):
  x=fixture();x['stages']['03']['beats'][0]['active_speaker']='D';self.assertIn('speaker absent',str(audit(x)))
 def test_anchor_absent(self):
  x=fixture();x['stages']['03']['beats'][0]['attention_anchor']='D';self.assertIn('anchor not grounded',str(audit(x)))
 def test_reaction_absent(self):
  x=fixture();x['stages']['03']['beats'][0]['reaction_targets']=['D'];self.assertIn('invalid reaction_targets',str(audit(x)))
 def test_drift_axis(self):
  x=fixture();x['stages']['04']['beats'][0]['screen_axis']='north-south';self.assertIn('drift screen_axis',str(audit(x)))
 def test_drift_reveal(self):
  x=fixture();x['stages']['05']['beats'][0]['reveal_order'].reverse();self.assertIn('drift reveal_order',str(audit(x)))
 def test_drift_knowledge(self):
  x=fixture();x['stages']['05']['beats'][0]['information_holders']=['B'];self.assertIn('drift information_holders',str(audit(x)))
 def test_missing_field(self):
  x=fixture();del x['stages']['03']['beats'][0]['blocking_state'];self.assertIn('missing blocking_state',str(audit(x)))
if __name__=='__main__':unittest.main()
