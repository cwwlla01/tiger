import hashlib, tempfile, unittest
from pathlib import Path
from ab_evidence_v226 import audit

class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.src=self.root/'source.md'; self.src.write_text('original',encoding='utf-8')
        self.data=dict(case_id='C1',source_path=str(self.src),source_sha256=hashlib.sha256(self.src.read_bytes()).hexdigest(),baseline_version='V2.24',candidate_version='V2.25',baseline_artifacts={},candidate_artifacts={})
    def test_source_only(self):
        self.assertEqual(audit(self.data)['evidence_level'],'SOURCE_ONLY')
    def test_no_comparison_without_pair(self):
        self.assertFalse(audit(self.data)['comparison_eligible'])
    def test_hash_mismatch(self):
        self.data['source_sha256']='0'*64
        with self.assertRaises(ValueError):audit(self.data)
    def test_baseline_only(self):
        for s in ('03','04','05'):
            p=self.root/('base'+s);p.write_text(s);self.data['baseline_artifacts'][s]=str(p)
        self.assertEqual(audit(self.data)['evidence_level'],'BASELINE_ONLY')
    def test_same_path_rejected(self):
        for s in ('03','04','05'):
            p=self.root/s;p.write_text(s);self.data['baseline_artifacts'][s]=str(p);self.data['candidate_artifacts'][s]=str(p)
        self.data['independent_run_evidence']={'baseline':'run1','candidate':'run2'}
        self.assertFalse(audit(self.data)['comparison_eligible'])
    def test_valid_pair(self):
        for side in ('baseline','candidate'):
            for s in ('03','04','05'):
                p=self.root/(side+s);p.write_text(side+s);self.data[side+'_artifacts'][s]=str(p)
        self.data['independent_run_evidence']={'baseline':'run1','candidate':'run2'}
        self.assertTrue(audit(self.data)['comparison_eligible'])
    def test_missing_provenance(self):
        for side in ('baseline','candidate'):
            for s in ('03','04','05'):
                p=self.root/(side+s);p.write_text(side+s);self.data[side+'_artifacts'][s]=str(p)
        self.assertFalse(audit(self.data)['comparison_eligible'])
    def test_missing_source(self):
        self.src.unlink()
        with self.assertRaises(ValueError):audit(self.data)
