import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_rehearsal import audit

ROOT=Path(__file__).resolve().parents[1] / 'tests' / 'fixtures'

class RehearsalAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.script=ROOT/'EP04_revision1.md'; self.plan=ROOT/'EP04_timing_plan.json'
        sh=hashlib.sha256(self.script.read_bytes()).hexdigest()
        ph=hashlib.sha256(self.plan.read_bytes()).hexdigest()
        t={'performed_at':'2026-10-29T10:00:00+01:00','operator':'sample tester',
           'measurement_method':'stopwatch','evidence_reference':'synthetic-fixture-not-real',
           'scene_seconds':[41,36,48],'transitions_and_pauses_seconds':4,
           'omitted_script_content':False,'all_physical_actions_performed':True,
           'all_dialogue_performed':True,'overlap_safety_checked':True}
        self.data={'episode':4,'script_sha256':sh,'plan_sha256':ph,'status':'performed',
                  'takes':[dict(t,take_id='fixture_A'),dict(t,take_id='fixture_B',evidence_reference='synthetic-fixture-B-not-real',scene_seconds=[43,35,49])]}
        self.path=Path(self.tmp.name)/'log.json'
    def run_audit(self):
        self.path.write_text(json.dumps(self.data),encoding='utf-8')
        return audit(self.script,self.plan,self.path)
    def test_synthetic_valid_metadata(self):self.assertTrue(self.run_audit()['mechanically_accepted'])
    def test_no_real_performance(self):
        self.data['status']='not_performed';self.assertFalse(self.run_audit()['mechanically_accepted'])
    def test_wrong_hash(self):
        self.data['script_sha256']='0'*64;self.assertIn('SOURCE_MISMATCH',self.run_audit()['issues'])
    def test_one_take(self):
        self.data['takes']=self.data['takes'][:1];self.assertFalse(self.run_audit()['mechanically_accepted'])
    def test_duplicate_take(self):
        self.data['takes'][1]['take_id']='fixture_A';self.assertFalse(self.run_audit()['mechanically_accepted'])
    def test_omitted_dialogue(self):
        self.data['takes'][0]['all_dialogue_performed']=False;self.assertFalse(self.run_audit()['mechanically_accepted'])
    def test_too_slow(self):
        self.data['takes'][0]['scene_seconds']=[80,80,80];self.assertFalse(self.run_audit()['mechanically_accepted'])
    def test_duplicate_evidence_reference(self):
        self.data['takes'][1]['evidence_reference'] = self.data['takes'][0]['evidence_reference']
        results=self.run_audit()
        self.assertFalse(results['mechanically_accepted'])
        self.assertIn('DUPLICATE_EVIDENCE_REFERENCE',results['take_results'][1]['issues'])
    def test_non_iso_timestamp(self):
        self.data['takes'][0]['performed_at']='a plausible but fake date'
        self.assertIn('INVALID_PERFORMED_AT',self.run_audit()['take_results'][0]['issues'])
    def test_timezone_missing(self):
        self.data['takes'][0]['performed_at']='2026-10-29T10:00:00'
        self.assertIn('INVALID_PERFORMED_AT',self.run_audit()['take_results'][0]['issues'])
    def test_independent_evidence_metadata(self):
        self.assertTrue(self.run_audit()['mechanically_accepted'])
    def test_bad_action(self):
        self.data['takes'][1]['overlap_safety_checked']=False;self.assertFalse(self.run_audit()['mechanically_accepted'])

if __name__=='__main__':unittest.main()
