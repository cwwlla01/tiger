import copy
import unittest
from audit_visual_state_v27 import audit

SHOT = {'take_id':'T-001','series_look_ref':'SERIES-A','scene_look_ref':'SCENE-A',
        'character_asset_ref':'CHAR-A','material_ref':'MAT-A','world_light_refs':['L1'],
        'camera':{'position':[0,0,2],'forward':[0,1,0]},
        'composition':{'type':'thirds'},'palette':'cool-white', 'weather':'indoor',
        'motion':{'start_s':0,'end_s':3},
        'face_light_claims':[{'light_id':'L1','status':'front_lit'}]}

def bundle():
    return {'schema_version':'2.7','stages':{s:{'takes':[copy.deepcopy(SHOT)]} for s in ('03','04','05')}}

class TestVisualState(unittest.TestCase):
    def test_valid(self): self.assertEqual(audit(bundle()),[])
    def test_missing_take(self):
        b=bundle();b['stages']['04']['takes']=[];self.assertTrue(audit(b))
    def test_changed_camera(self):
        b=bundle();b['stages']['05']['takes'][0]['camera']['position']=[1,0,2];self.assertTrue(audit(b))
    def test_changed_light(self):
        b=bundle();b['stages']['04']['takes'][0]['world_light_refs']=['L2'];self.assertTrue(audit(b))
    def test_bad_light_claim(self):
        b=bundle();b['stages']['03']['takes'][0]['face_light_claims'][0]['light_id']='UNKNOWN';self.assertTrue(audit(b))
    def test_duplicate(self):
        b=bundle();b['stages']['03']['takes'].append(copy.deepcopy(SHOT));self.assertTrue(audit(b))
    def test_missing_stage(self):
        b=bundle();del b['stages']['05'];self.assertTrue(audit(b))
    def test_changed_material(self):
        b=bundle();b['stages']['05']['takes'][0]['material_ref']='MAT-B';self.assertTrue(audit(b))

if __name__=='__main__': unittest.main()
