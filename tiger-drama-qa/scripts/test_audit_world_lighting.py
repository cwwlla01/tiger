import unittest
from audit_world_lighting import audit

BASE={'lights':[{'id':'wall','position':[2,0,2]}], 'takes':[
 {'id':'front','camera':{'position':[0,-4,1.5],'target':[0,0,1.5]},'subject_position':[0,0,1], 'light_claims':[{'light_id':'wall','screen_side':'right'}]},
 {'id':'reverse','camera':{'position':[0,4,1.5],'target':[0,0,1.5]},'subject_position':[0,0,1], 'light_claims':[{'light_id':'wall','screen_side':'left'}]}]}

class WorldLightingTests(unittest.TestCase):
 def test_reverse_side_flips(self): self.assertTrue(audit(BASE)['passed'])
 def test_wrong_screen_side(self):
  import copy
  d=copy.deepcopy(BASE);d['takes'][1]['light_claims'][0]['screen_side']='right';self.assertFalse(audit(d)['passed'])
 def test_moved_fixed_light(self):
  import copy
  d=copy.deepcopy(BASE);d['takes'][0]['light_claims'][0]['world_position']=[-2,0,2];self.assertFalse(audit(d)['passed'])
 def test_unknown_light(self):
  import copy
  d=copy.deepcopy(BASE);d['takes'][0]['light_claims'][0]['light_id']='ghost';self.assertFalse(audit(d)['passed'])
 def test_degenerate_camera(self):
  import copy
  d=copy.deepcopy(BASE);d['takes'][0]['camera']['target']=[0,-4,1.5];self.assertFalse(audit(d)['passed'])

if __name__=='__main__':unittest.main()
