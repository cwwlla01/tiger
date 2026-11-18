import unittest
from audit_light_zone_crossing import audit


def fixture():
    return {'zones':[{'id':'door_warm','center':[2,0,1],'radius':1}], 'takes':[{'id':'T-01','samples':[{'time_s':0,'position':[0,0,1]},{'time_s':1,'position':[1.5,0,1]},{'time_s':2,'position':[2,0,1]}], 'zone_claims':[{'zone_id':'door_warm','start_inside':False,'end_inside':True,'transition_count':1,'first_transition':'enter'}]}]}

class Tests(unittest.TestCase):
    def test_valid_entry(self): self.assertTrue(audit(fixture())['passed'])
    def test_wrong_transition(self):
        x=fixture();x['takes'][0]['zone_claims'][0]['transition_count']=0
        self.assertFalse(audit(x)['passed'])
    def test_wrong_end(self):
        x=fixture();x['takes'][0]['zone_claims'][0]['end_inside']=False
        self.assertFalse(audit(x)['passed'])
    def test_unknown_zone(self):
        x=fixture();x['takes'][0]['zone_claims'][0]['zone_id']='fake'
        self.assertFalse(audit(x)['passed'])
    def test_invalid_time(self):
        x=fixture();x['takes'][0]['samples'][1]['time_s']=0
        self.assertFalse(audit(x)['passed'])

if __name__=='__main__': unittest.main()
