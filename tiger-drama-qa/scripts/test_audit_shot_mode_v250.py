import unittest
from audit_shot_mode_v250 import validate_route, audit_routes
class TestRouting(unittest.TestCase):
 def route(self,mode,inputs=None,supported=None): return {"mode":mode,"inputs":inputs or {},"supported_modes":supported if supported is not None else [mode]}
 def test_text_no_frame(self): self.assertEqual(validate_route(self.route("TEXT_TO_VIDEO"))["status"],"ROUTE_READY_TEXT_ONLY")
 def test_reference_ready(self): self.assertEqual(validate_route(self.route("REFERENCE_TO_VIDEO",{"reference":{"verified":True}}))["status"],"ROUTE_READY_TEXT_ONLY")
 def test_reference_missing(self): self.assertEqual(validate_route(self.route("REFERENCE_TO_VIDEO"))["missing"],["reference"])
 def test_first_missing(self): self.assertEqual(validate_route(self.route("FIRST_FRAME_TO_VIDEO"))["missing"],["first_frame"])
 def test_first_ready(self): self.assertEqual(validate_route(self.route("FIRST_FRAME_TO_VIDEO",{"first_frame":{"verified":True}}))["status"],"ROUTE_READY_TEXT_ONLY")
 def test_both_missing(self): self.assertEqual(len(validate_route(self.route("FIRST_LAST_FRAME_TO_VIDEO"))["missing"]),2)
 def test_last_missing(self): self.assertEqual(validate_route(self.route("FIRST_LAST_FRAME_TO_VIDEO",{"first_frame":{"verified":True}}))["missing"],["last_frame"])
 def test_both_ready(self): self.assertEqual(validate_route(self.route("FIRST_LAST_FRAME_TO_VIDEO",{"first_frame":{"verified":True},"last_frame":{"verified":True}}))["status"],"ROUTE_READY_TEXT_ONLY")
 def test_unsupported(self): self.assertEqual(validate_route(self.route("FIRST_FRAME_TO_VIDEO",supported=["TEXT_TO_VIDEO"]))["status"],"ROUTE_CAPABILITY_UNVERIFIED")
 def test_unknown(self): self.assertEqual(validate_route(self.route("MAGIC"))["status"],"ROUTE_INVALID")
 def test_batch(self): self.assertEqual(len(audit_routes([dict(self.route("TEXT_TO_VIDEO"),shot="S01"),dict(self.route("TEXT_TO_VIDEO"),shot="S02")])),2)
