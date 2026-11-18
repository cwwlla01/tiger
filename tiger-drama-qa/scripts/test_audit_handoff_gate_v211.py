import unittest
from audit_handoff_gate_v211 import audit

class GateTest(unittest.TestCase):
    def test_clean_director(self):
        self.assertTrue(audit({'takes':[{'take_id':'T-1','stage':'03'}]})['pass'])
    def test_uncertain_geometry_fallback(self):
        self.assertIn('MISSING_FALLBACK', self.codes({'takes':[{'take_id':'T-1','geometry_uncertain':True}]}))
    def test_fallback_resolves(self):
        self.assertTrue(audit({'takes':[{'take_id':'T-1','geometry_uncertain':True,'fallback_shot':'fixed insert'}]})['pass'])
    def test_simulation_loop(self):
        self.assertIn('SIMULATION_LOOP',self.codes({'takes':[{'take_id':'T-1','simulation_rounds':3}]}))
    def test_new_evidence_allows_retry(self):
        self.assertTrue(audit({'takes':[{'take_id':'T-1','simulation_rounds':3,'new_authoritative_evidence':True}]})['pass'])
    def test_unfrozen_formal(self):
        self.assertIn('UNFROZEN_FORMAL',self.codes({'director_hash':'abc','takes':[{'take_id':'T-1','stage':'04','delivery_status':'FORMAL','director_hash':'abc'}]}))
    def test_candidate_allowed(self):
        self.assertTrue(audit({'director_hash':'abc','takes':[{'take_id':'T-1','stage':'04','delivery_status':'CANDIDATE','director_hash':'abc'}]})['pass'])
    def test_hash_mismatch(self):
        self.assertIn('DIRECTOR_VERSION_MISMATCH',self.codes({'director_frozen':True,'director_hash':'abc','takes':[{'take_id':'T-1','stage':'05','director_hash':'def'}]}))
    def test_unapproved_redirection(self):
        self.assertIn('UNAPPROVED_REDIRECT',self.codes({'director_frozen':True,'director_hash':'abc','takes':[{'take_id':'T-1','stage':'05','director_hash':'abc','unapproved_director_change':True}]}))
    def test_no_fake_video_qa(self):
        self.assertIn('UNSUPPORTED_VIDEO_PASS',self.codes({'takes':[{'take_id':'T-1','claims_video_qa_passed':True}]}))
    def test_video_evidence(self):
        self.assertTrue(audit({'takes':[{'take_id':'T-1','claims_video_qa_passed':True,'evidence':{'video_review':'review-id'}}]})['pass'])
    def test_no_fake_asset(self):
        self.assertIn('UNSUPPORTED_ASSET_PASS',self.codes({'takes':[{'take_id':'T-1','claims_asset_verified':True}]}))
    def test_no_fake_physics(self):
        self.assertIn('SIMULATION_OVERCLAIM',self.codes({'takes':[{'take_id':'T-1','claims_physics_verified':True,'evidence':{'physics':'simulation'}}]}))
    def test_duplicate(self):
        self.assertIn('DUPLICATE_TAKE',self.codes({'takes':[{'take_id':'T-1'},{'take_id':'T-1'}]}))
    def test_canon_conflict(self):
        self.assertIn('CANON_CONFLICT',self.codes({'takes':[{'take_id':'T-1','canonical_conflict':True}]}))
    def codes(self, data):
        return {x['code'] for x in audit(data)['issues']}
if __name__ == '__main__': unittest.main()
