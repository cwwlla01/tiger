import unittest
from benchmark_skill_v225 import metrics, compare

class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.case = {"case_id":"synthetic", "evidence_level":"FIXTURE_ONLY", "source_sha256":"a"*64,
          "baseline_version":"V2.24", "candidate_version":"V2.25",
          "baseline":{"source_beat_ids":["b1","b2"],"generated_beat_ids":["b1"],"prompts":["Look", " look  "]},
          "candidate":{"source_beat_ids":["b1","b2"],"generated_beat_ids":["b1","b2"],"prompts":["Look","Run"]}}
    def test_pair(self):
        r=compare(self.case); self.assertEqual(r["baseline"]["beat_coverage"],0.5)
        self.assertEqual(r["candidate"]["beat_coverage"],1)
    def test_redundancy(self): self.assertEqual(metrics(self.case["baseline"])["prompt_redundancy"],0.5)
    def test_no_source(self):
        c={"source_beat_ids":[],"generated_beat_ids":[],"prompts":[]}
        self.assertEqual(metrics(c)["beat_coverage"],"NOT_VERIFIED")
    def test_unsupported(self):
        c={"source_beat_ids":["a"],"generated_beat_ids":["a","x"],"prompts":[]}
        self.assertEqual(metrics(c)["unsupported_addition_ids"],["x"])
    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError): metrics({"source_beat_ids":["a","a"],"generated_beat_ids":[],"prompts":[]})
    def test_mismatched_source_rejected(self):
        self.case["candidate"]["source_beat_ids"]=["other"]
        with self.assertRaises(ValueError): compare(self.case)
    def test_qa_requires_gold(self):
        self.assertEqual(metrics(self.case["candidate"])["qa_precision"],"NOT_VERIFIED")
    def test_qa_precision(self):
        self.case["candidate"]["qa_confusion"]={"tp":3,"fp":1,"fn":2}
        r=metrics(self.case["candidate"])
        self.assertEqual(r["qa_precision"],0.75); self.assertEqual(r["qa_recall"],0.6)
    def test_negative_qa_rejected(self):
        self.case["candidate"]["qa_confusion"]={"tp":-1,"fp":0,"fn":0}
        with self.assertRaises(ValueError): metrics(self.case["candidate"])
    def test_evidence_guard(self):
        self.assertIs(compare(self.case)["production_quality_verified"],False)
    def test_missing_evidence_rejected(self):
        self.case.pop("evidence_level")
        with self.assertRaises(ValueError): compare(self.case)
    def test_bad_hash_rejected(self):
        self.case["source_sha256"]="fake"
        with self.assertRaises(ValueError): compare(self.case)
