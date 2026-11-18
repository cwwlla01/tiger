import tempfile
import unittest
from pathlib import Path
from audit_scene_evidence_v238 import audit,sha256_file

class SceneEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); d=Path(self.tmp.name)
        self.a=d/'a.md';self.b=d/'b.md';self.a.write_text('A');self.b.write_text('B')
        self.old={'source_sha256':'source','skill_version':'V2.37','run_id':'run-a','output_sha256':sha256_file(self.a),'output_path':str(self.a),'run_conditions':{'model':'fixed'}}
        self.new=dict(self.old,skill_version='V2.38',run_id='run-b',output_sha256=sha256_file(self.b),output_path=str(self.b))
    def tearDown(self):self.tmp.cleanup()
    def test_valid_evidence(self):self.assertEqual(audit(self.old,self.new)['status'],'COMPARABLE_FOR_REVIEW')
    def test_no_artistic_claim(self):self.assertEqual(audit(self.old,self.new)['artistic_quality'],'NOT_VERIFIED')
    def test_missing_run(self):self.assertEqual(audit(self.old,None)['status'],'NOT_COMPARABLE')
    def test_wrong_type(self):self.assertIn('INVALID_RECORD',audit([],self.new)['issues'])
    def test_different_source(self):self.assertIn('DIFFERENT_SOURCE',audit(self.old,dict(self.new,source_sha256='other'))['issues'])
    def test_same_run(self):self.assertIn('NOT_INDEPENDENT_RUNS',audit(self.old,dict(self.new,run_id='run-a'))['issues'])
    def test_shared_path(self):self.assertIn('SHARED_OUTPUT_PATH',audit(self.old,dict(self.new,output_path=str(self.a)))['issues'])
    def test_same_version(self):self.assertIn('SAME_SKILL_VERSION',audit(self.old,dict(self.new,skill_version='V2.37'))['issues'])
    def test_changed_conditions(self):self.assertIn('DIFFERENT_RUN_CONDITIONS',audit(self.old,dict(self.new,run_conditions={'model':'other'}))['issues'])
    def test_hash_mismatch(self):self.assertIn('CANDIDATE_HASH_MISMATCH',audit(self.old,dict(self.new,output_sha256='bad'))['issues'])
    def test_missing_file(self):self.assertIn('CANDIDATE_OUTPUT_NOT_FOUND',audit(self.old,dict(self.new,output_path='/nonexistent/does-not-exist'))['issues'])
    def test_fixture_rejected(self):self.assertIn('CANDIDATE_SYNTHETIC_FIXTURE',audit(self.old,dict(self.new,evidence_level='SYNTHETIC_FIXTURE'))['issues'])
if __name__=='__main__':unittest.main()
