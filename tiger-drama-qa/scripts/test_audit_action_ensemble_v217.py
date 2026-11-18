import copy
import unittest
from audit_action_ensemble_v217 import audit

B={'beat_id':'B01','source_anchor':'scene1:line3','action':'甲扶起乙','take_ids':['T01'],'actor_ids':['A','B'],'target_ids':['B'],'prop_custody_before':{'rope':'A'},'prop_custody_after':{'rope':'B'},'screen_direction':'left-to-right','contact_event':'A grips B wrist','observable_end_state':'B standing','knowledge_after':{'A':['B safe'],'B':['A helped']}}

def bundle():
    return {'stages':{s:{'beats':[copy.deepcopy(B)]} for s in ('03','04','05')}}

class AuditTest(unittest.TestCase):
    def test_valid(self):self.assertTrue(audit(bundle())['passed'])
    def test_missing_beat(self):
        b=bundle();b['stages']['05']['beats']=[];self.assertIn('05:B01: MISSING_BEAT',audit(b)['issues'])
    def test_prop_drift(self):
        b=bundle();b['stages']['04']['beats'][0]['prop_custody_after']={'rope':'A'};self.assertFalse(audit(b)['passed'])
    def test_contact_drift(self):
        b=bundle();b['stages']['05']['beats'][0]['contact_event']='none';self.assertFalse(audit(b)['passed'])
    def test_direction_drift(self):
        b=bundle();b['stages']['05']['beats'][0]['screen_direction']='right-to-left';self.assertFalse(audit(b)['passed'])
    def test_identity_drift(self):
        b=bundle();b['stages']['04']['beats'][0]['actor_ids']=['C'];self.assertFalse(audit(b)['passed'])
    def test_unsourced(self):
        b=bundle();x=copy.deepcopy(B);x['beat_id']='B02';b['stages']['05']['beats'].append(x);self.assertFalse(audit(b)['passed'])
    def test_duplicate(self):
        b=bundle();b['stages']['03']['beats'].append(copy.deepcopy(B));self.assertFalse(audit(b)['passed'])
    def test_missing_required(self):
        b=bundle();del b['stages']['03']['beats'][0]['source_anchor'];self.assertFalse(audit(b)['passed'])
    def test_knowledge_drift(self):
        b=bundle();b['stages']['05']['beats'][0]['knowledge_after']={};self.assertFalse(audit(b)['passed'])

if __name__=='__main__':unittest.main()
