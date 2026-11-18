import unittest
from copy import deepcopy
from audit_edit_continuity_v220 import audit
BASE={'shot_order':['A','B'],'03':[{'edit_link_id':'E1','from_shot_id':'A','to_shot_id':'B','cut_intent':'reaction','cut_type':'STRAIGHT','reveal_boundary':'PRESERVE','handoff_status':'READY'}]}
def sample():
 d=deepcopy(BASE);d['04']=deepcopy(d['03']);d['05']=deepcopy(d['03']);return d
class TestEditContinuity(unittest.TestCase):
 def test_clean(self):self.assertEqual(audit(sample()),[])
 def test_missing_id(self):
  d=sample();d['03'][0]['edit_link_id']='';self.assertIn('duplicate_or_missing_link_id',audit(d))
 def test_nonadjacent(self):
  d=sample();d['shot_order']=['A','X','B'];self.assertIn('nonadjacent_shots',audit(d))
 def test_invalid_type(self):
  d=sample();d['03'][0]['cut_type']='MAGIC';self.assertIn('invalid_cut_type',audit(d))
 def test_action_match(self):
  d=sample();d['03'][0]['cut_type']='MATCH_ACTION';self.assertIn('missing_action_match',audit(d))
 def test_eyeline(self):
  d=sample();d['03'][0]['cut_type']='EYELINE';self.assertIn('missing_eyeline',audit(d))
 def test_sound_bridge(self):
  d=sample();d['03'][0]['cut_type']='SOUND_BRIDGE';self.assertIn('missing_sound_bridge',audit(d))
 def test_missing_04(self):
  d=sample();d['04']=[];self.assertIn('04_link_coverage',audit(d))
 def test_drift_05(self):
  d=sample();d['05'][0]['reveal_boundary']='REVEAL_AT_CUT';self.assertIn('05_contract_drift',audit(d))
 def test_invalid_status(self):
  d=sample();d['03'][0]['handoff_status']='PASS';self.assertIn('invalid_handoff_status',audit(d))
