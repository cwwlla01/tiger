import copy,unittest
from audit_face_lighting import audit

BASE={'lights':[{'id':'L','position':[2,0,1]}],'obstacles':[], 'takes':[{'id':'T','samples':[{'time_s':0,'face_position':[0,0,1],'face_forward':[1,0,0],'light_claims':[{'light_id':'L','expected_face_status':'front_lit'}]}]}]}
class FaceLightingTests(unittest.TestCase):
    def test_front(self): self.assertTrue(audit(BASE)['passed'])
    def test_back_facing(self):
        x=copy.deepcopy(BASE);x['takes'][0]['samples'][0]['face_forward']=[-1,0,0];self.assertFalse(audit(x)['passed'])
    def test_occluded(self):
        x=copy.deepcopy(BASE);x['obstacles']=[{'min':[0.8,-0.2,0.5],'max':[1.2,0.2,1.5]}];x['takes'][0]['samples'][0]['light_claims'][0]['expected_face_status']='occluded';self.assertTrue(audit(x)['passed'])
    def test_bad_occlusion_claim(self):
        x=copy.deepcopy(BASE);x['obstacles']=[{'min':[0.8,-0.2,0.5],'max':[1.2,0.2,1.5]}];self.assertFalse(audit(x)['passed'])
    def test_transparent(self):
        x=copy.deepcopy(BASE);x['obstacles']=[{'min':[0.8,-0.2,0.5],'max':[1.2,0.2,1.5],'opaque':False}];self.assertTrue(audit(x)['passed'])
    def test_zero_facing(self):
        x=copy.deepcopy(BASE);x['takes'][0]['samples'][0]['face_forward']=[0,0,0];self.assertFalse(audit(x)['passed'])
if __name__=='__main__':unittest.main()
