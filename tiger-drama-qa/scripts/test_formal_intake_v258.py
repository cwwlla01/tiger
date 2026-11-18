import unittest
from audit_formal_intake_v258 import audit
class FormalIntakeTests(unittest.TestCase):
 def test_no_script_global_block(self): self.assertEqual(audit({})["status"],"GLOBAL_SOURCE_BLOCK")
 def test_test_script_not_authority(self): self.assertEqual(audit({"source_type":"TEST_SCRIPT_ONLY","authoritative_script":"sample"})["status"],"GLOBAL_SOURCE_BLOCK")
 def test_formal_incomplete(self): self.assertEqual(audit({"source_type":"FORMAL_AUTHORITY","authoritative_script":"a"})["status"],"FORMAL_INTAKE_INCOMPLETE")
 def test_no_video_no_acceptance(self):
  d={k:"verified" for k in ("authoritative_script","script_version","asset_manifest","storyboard_03","static_prompts_04","video_prompts_05","independent_qa_06")};d["source_type"]="FORMAL_AUTHORITY"
  self.assertEqual(audit(d)["status"],"TEXT_INTAKE_COMPLETE_VIDEO_UNTESTED")
  self.assertFalse(audit(d)["production_accepted"])
 def test_local_block_retained(self): self.assertEqual(audit({"known_local_blocks":["S07_LAYOUT_UNVERIFIED"]})["local_blocks"],["S07_LAYOUT_UNVERIFIED"])
 def test_video_evidence_not_auto_acceptance(self):
  d={k:"x" for k in ("authoritative_script","script_version","asset_manifest","storyboard_03","static_prompts_04","video_prompts_05","independent_qa_06","video_evidence")};d["source_type"]="FORMAL_AUTHORITY"
  self.assertEqual(audit(d)["status"],"EVIDENCE_SUBMITTED_REQUIRES_INDEPENDENT_REVIEW")
  self.assertFalse(audit(d)["production_accepted"])
