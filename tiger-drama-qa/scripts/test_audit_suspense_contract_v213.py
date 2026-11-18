import unittest
from copy import deepcopy
from audit_suspense_contract_v213 import audit
BASE={'source_beats':[{'id':'B1','anchor':'line1','must_precede':['B2']},{'id':'B2','anchor':'line2'}], 'stages':{'03':[{'take_id':'T1','beat_ids':['B1'],'reveal_policy':'REACTION_ONLY'},{'take_id':'T2','beat_ids':['B2'],'reveal_policy':'SHOW'}], '04':[{'take_id':'T1','beat_ids':['B1'],'reveal_policy':'REACTION_ONLY'},{'take_id':'T2','beat_ids':['B2'],'reveal_policy':'SHOW'}], '05':[{'take_id':'T1','beat_ids':['B1'],'reveal_policy':'REACTION_ONLY'},{'take_id':'T2','beat_ids':['B2'],'reveal_policy':'SHOW'}]}}
class TestV213(unittest.TestCase):
 def test_valid(self): self.assertEqual(audit(deepcopy(BASE)),[])
 def test_missing_beat(self):
  x=deepcopy(BASE);x['stages']['03'][1]['beat_ids']=[];self.assertTrue(any('BEAT_MISSING' in s for s in audit(x)))
 def test_order(self):
  x=deepcopy(BASE);x['stages']['03'].reverse();self.assertTrue(any('ORDER_BROKEN' in s for s in audit(x)))
 def test_policy_drift(self):
  x=deepcopy(BASE);x['stages']['05'][0]['reveal_policy']='SHOW';self.assertTrue(any('DRIFT:05' in s for s in audit(x)))
 def test_beat_drift(self):
  x=deepcopy(BASE);x['stages']['04'][0]['beat_ids']=['B2'];self.assertTrue(any('DRIFT:04' in s for s in audit(x)))
 def test_missing_take(self):
  x=deepcopy(BASE);x['stages']['05'].pop();self.assertTrue(any('TAKE_MISSING' in s for s in audit(x)))
 def test_missing_anchor(self):
  x=deepcopy(BASE);x['source_beats'][0]['anchor']='';self.assertIn('SOURCE_BEATS_INVALID',audit(x))
 def test_invalid_policy(self):
  x=deepcopy(BASE);x['stages']['03'][0]['reveal_policy']='SURPRISE';self.assertTrue(any('POLICY_INVALID' in s for s in audit(x)))
 def test_unknown_beat(self):
  x=deepcopy(BASE);x['stages']['03'][0]['beat_ids'].append('B9');self.assertTrue(any('UNKNOWN_BEAT' in s for s in audit(x)))
if __name__=='__main__': unittest.main()
