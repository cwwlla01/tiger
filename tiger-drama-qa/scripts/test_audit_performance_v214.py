import unittest
from audit_performance_v214 import audit

def fixture():
 p={'source_anchor':'S1','character_id':'C1','objective':'离开','obstacle':'门外响动','knowledge_before':'未知','knowledge_after':'仍未知','beats':[{'beat_id':'b1','observable_action':'右手悬停','start_state':'抬手','end_state':'悬停'},{'beat_id':'b2','observable_action':'后退','start_state':'站立','end_state':'退一步'}]}
 return {'stages':{'03':{'takes':[{'take_id':'T1','performance':p}]},'04':{'takes':[{'take_id':'T1','performance':dict(p,beats=p['beats'][:1])}]},'05':{'takes':[{'take_id':'T1','performance':dict(p)}]}}}
class TestPerformance(unittest.TestCase):
 def test_valid(self):self.assertEqual(audit(fixture()),[])
 def test_missing_objective(self):
  b=fixture();b['stages']['03']['takes'][0]['performance']['objective']='';self.assertTrue(any('MISSING_objective' in x for x in audit(b)))
 def test_missing_beats(self):
  b=fixture();b['stages']['03']['takes'][0]['performance']['beats']=[];self.assertTrue(any('INVALID_BEATS' in x for x in audit(b)))
 def test_duplicate_beats(self):
  b=fixture();p=b['stages']['03']['takes'][0]['performance'];p['beats'].append(dict(p['beats'][0]));self.assertTrue(any('INVALID_BEATS' in x for x in audit(b)))
 def test_unobservable(self):
  b=fixture();b['stages']['03']['takes'][0]['performance']['beats'][0]['observable_action']='';self.assertTrue(any('UNOBSERVABLE_BEAT' in x for x in audit(b)))
 def test_character_drift(self):
  b=fixture();b['stages']['05']['takes'][0]['performance']['character_id']='C2';self.assertTrue(any('CHARACTER_DRIFT' in x for x in audit(b)))
 def test_knowledge_drift(self):
  b=fixture();b['stages']['05']['takes'][0]['performance']['knowledge_after']='知道真相';self.assertTrue(any('KNOWLEDGE_DRIFT' in x for x in audit(b)))
 def test_order_drift(self):
  b=fixture();p=b['stages']['05']['takes'][0]['performance'];p['beats']=list(reversed(p['beats']));self.assertTrue(any('BEAT_ORDER_DRIFT' in x for x in audit(b)))
 def test_frame_invention(self):
  b=fixture();b['stages']['04']['takes'][0]['performance']['beats']=[{'beat_id':'new'}];self.assertTrue(any('FRAME_BEAT_INVENTED' in x for x in audit(b)))
 def test_missing_compilation(self):
  b=fixture();b['stages']['05']['takes'][0].pop('performance');self.assertTrue(any('PERFORMANCE_MISSING' in x for x in audit(b)))
