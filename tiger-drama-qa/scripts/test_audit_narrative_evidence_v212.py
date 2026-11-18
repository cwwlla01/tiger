import unittest
from audit_narrative_evidence_v212 import audit
GOOD={'source_anchor':'L12','shot_id':'T-003','observed_issue':'线索提前出现','audience_impact':'悬念消失','minimal_fix':'延后特写','confidence':'high','severity':'P2'}
class TestNarrativeEvidence(unittest.TestCase):
 def test_valid(self): self.assertEqual(audit({'findings':[GOOD],'status':'DRAFT'}),[])
 def test_missing_source(self): self.assertTrue(audit({'findings':[dict(GOOD,source_anchor='')]}))
 def test_missing_impact(self): self.assertTrue(audit({'findings':[dict(GOOD,audience_impact='')]}))
 def test_invalid_severity(self): self.assertTrue(audit({'findings':[dict(GOOD,severity='P9')]}))
 def test_unreviewed_pass(self): self.assertTrue(audit({'status':'TEXT_REVIEW_PASS'}))
 def test_reviewed_pass(self): self.assertFalse(audit({'status':'TEXT_REVIEW_PASS','independent_reviewer_evidence':'report.pdf'}))
 def test_blocker(self): self.assertTrue(audit({'status':'TEXT_REVIEW_PASS','independent_reviewer_evidence':'report.pdf','findings':[dict(GOOD,severity='P1')]}))
 def test_video_without_footage(self): self.assertTrue(audit({'status':'VIDEO_QA_PASSED','independent_reviewer_evidence':'review'}))
 def test_video_with_footage(self): self.assertFalse(audit({'status':'VIDEO_QA_PASSED','independent_reviewer_evidence':'review','footage_evidence':'video.mp4'}))
if __name__=='__main__': unittest.main()
