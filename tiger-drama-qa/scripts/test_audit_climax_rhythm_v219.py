import unittest,copy
from audit_climax_rhythm_v219 import audit,FIELDS

def fixture():
 b=dict(sequence_id='S1',beat_id='B1',source_event_ids=['E1'],dramatic_function='REVERSAL',tempo_intent='BURST',focus_owner='A',attention_transition='A>B',threat_delta='rises',reversal_trigger='door closes',state_before='open',state_after='closed',cost_paid='injury',result_evidence='door shut')
 return {'stages':{s:{'beats':[copy.deepcopy(b)]} for s in ('03','04','05')}}
class TestClimax(unittest.TestCase):
 def test_clean(self):self.assertEqual(audit(fixture()),[])
 def test_missing_anchor(self):
  d=fixture();d['stages']['03']['beats'][0]['source_event_ids']=[];self.assertTrue(any('source anchors' in x for x in audit(d)))
 def test_missing_trigger(self):
  d=fixture();d['stages']['03']['beats'][0]['reversal_trigger']='NONE';self.assertTrue(any('reversal lacks trigger' in x for x in audit(d)))
 def test_payoff_evidence(self):
  d=fixture();[x['beats'][0].update(dramatic_function='PAYOFF',result_evidence='NONE') for x in d['stages'].values()];self.assertTrue(any('payoff lacks evidence' in x for x in audit(d)))
 def test_tempo_drift(self):
  d=fixture();d['stages']['05']['beats'][0]['tempo_intent']='HOLD';self.assertTrue(any('drift tempo_intent' in x for x in audit(d)))
 def test_focus_drift(self):
  d=fixture();d['stages']['04']['beats'][0]['focus_owner']='B';self.assertTrue(any('drift focus_owner' in x for x in audit(d)))
 def test_state_drift(self):
  d=fixture();d['stages']['05']['beats'][0]['state_after']='open';self.assertTrue(any('drift state_after' in x for x in audit(d)))
 def test_missing_beat(self):
  d=fixture();d['stages']['04']['beats']=[];self.assertTrue(any('missing beat' in x for x in audit(d)))
 def test_extra_beat(self):
  d=fixture();d['stages']['05']['beats'].append(dict(d['stages']['05']['beats'][0],beat_id='B2'));self.assertTrue(any('extra beat' in x for x in audit(d)))
 def test_order_drift(self):
  d=fixture();[x['beats'].append(dict(x['beats'][0],beat_id='B2')) for x in d['stages'].values()];d['stages']['05']['beats'].reverse();self.assertTrue(any('order drift' in x for x in audit(d)))
