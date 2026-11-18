import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from continuity_coverage import scan,audit

SCRIPT='''## EP02\n### SC01｜医院｜夜｜内\n△周宁捏着钥匙，看到阿砚手上仍有割伤。\n周宁：我不知道谁换了钥匙。\n△两人离开医院。\n'''

class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/'EP02.md';self.path.write_text(SCRIPT,encoding='utf-8')
        self.sc=scan(self.path)
    def review(self):
        return {'script_sha256':self.sc['script_sha256'],
          'editor_full_read_attestation':'我已逐行阅读整集剧本并检查候选以外的连续性信息。',
          'dispositions':[{'id':x['id'],'decision':'track','reason':'这一处对象变化需要后续剧集明确持续追踪。','state_key':'道具.钥匙'} for x in self.sc['candidates']]}
    def test_candidates(self):
        self.assertEqual(len(self.sc['candidates']),2)
        self.assertFalse(self.sc['coverage_is_exhaustive'])
    def test_priority_batches_preserve_every_candidate(self):
        from continuity_coverage import build_review_batches
        all_ids = [x['id'] for x in self.sc['candidates']]
        grouped = [cid for batch in self.sc['review_batches'] for cid in batch['candidate_ids']]
        self.assertCountEqual(grouped, all_ids)
        self.assertEqual(len(grouped), len(set(grouped)))
        self.assertEqual(sum(self.sc['priority_counts'].values()), len(all_ids))

    def test_generic_knowledge_phrase_not_independent_candidate(self):
        self.path.write_text('### SC01｜房间｜夜｜内\n周宁：我不知道。\n△他看了她一眼。\n',encoding='utf-8')
        self.assertEqual(scan(self.path)['candidates'], [])

    def test_important_new_health_and_custody_stay_high(self):
        self.path.write_text('### SC01｜房间｜夜｜内\n△周宁割伤手指，把照片交给民警。\n',encoding='utf-8')
        result=scan(self.path)
        self.assertEqual(len(result['candidates']),1)
        self.assertIn('injury_health',result['candidates'][0]['categories'])
        self.assertIn('object_custody',result['candidates'][0]['categories'])
        self.assertEqual(result['candidates'][0]['priority'],'high')

    def test_passive_prop_stage_direction_is_not_high(self):
        self.path.write_text('### SC01｜室内｜夜｜内\n△周宁拿着照片，瞥向手机。\n',encoding='utf-8')
        result=scan(self.path)
        self.assertEqual(len(result['candidates']),1)
        self.assertEqual(result['candidates'][0]['priority'],'review')

    def test_prop_transfer_stage_direction_remains_high(self):
        self.path.write_text('### SC01｜室内｜夜｜内\n△周宁把照片交给民警。\n',encoding='utf-8')
        result=scan(self.path)
        self.assertEqual(len(result['candidates']),1)
        self.assertEqual(result['candidates'][0]['priority'],'high')

    def test_injury_stage_direction_remains_high(self):
        self.path.write_text('### SC01｜室内｜夜｜内\n△周宁的手指流血，手机滑落。\n',encoding='utf-8')
        self.assertEqual(scan(self.path)['candidates'][0]['priority'],'high')

    def test_reprioritization_keeps_candidate_ids_and_audit(self):
        self.path.write_text('### SC01｜室内｜夜｜内\n△周宁拿着照片。\n△周宁把照片交给民警。\n',encoding='utf-8')
        self.sc=scan(self.path)
        self.assertEqual(self.sc['priority_counts'],{'high':1,'review':1})
        self.assertTrue(audit(self.sc,self.review())['coverage_review_complete'])

    def test_batch_does_not_allow_skipping_individual_review(self):
        r=self.review(); r['dispositions'].pop()
        self.assertFalse(audit(self.sc,r)['coverage_review_complete'])

    def test_valid(self):self.assertTrue(audit(self.sc,self.review())['coverage_review_complete'])
    def test_omission(self):
        r=self.review();r['dispositions'].pop();self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def test_duplicate(self):
        r=self.review();r['dispositions'].append(r['dispositions'][0]);self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def test_deferred(self):
        r=self.review();r['dispositions'][0]['decision']='defer';self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def test_hash(self):
        r=self.review();r['script_sha256']='0'*64;self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def test_no_attestation(self):
        r=self.review();r['editor_full_read_attestation']='';self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def test_unsupported_id(self):
        r=self.review();r['dispositions'][0]['id']='madeup';self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def test_no_key(self):
        r=self.review();r['dispositions'][0]['state_key']='';self.assertFalse(audit(self.sc,r)['coverage_review_complete'])
    def ledger(self):
        return {'current_sha256':self.sc['script_sha256'],
                'current_state':{'道具.钥匙':'周宁持有'},
                'introduced':[{'key':'道具.钥匙'}]}
    def test_linked_new_tracking_passes(self):
        self.assertTrue(audit(self.sc,self.review(),self.ledger())['coverage_review_complete'])
    def test_fabricated_tracking_key_blocked(self):
        ledger=self.ledger();ledger['current_state']={}
        result=audit(self.sc,self.review(),ledger)
        self.assertFalse(result['coverage_review_complete'])
        self.assertTrue(any(x.startswith('STATE_KEY_NOT_IN_LEDGER') for x in result['errors']))
    def test_new_tracking_not_introduced_blocked(self):
        ledger=self.ledger();ledger['introduced']=[]
        self.assertFalse(audit(self.sc,self.review(),ledger)['coverage_review_complete'])
    def test_existing_tracking_allowed(self):
        r=self.review()
        for e in r['dispositions']:e['decision']='already_tracked'
        ledger=self.ledger();ledger['introduced']=[]
        self.assertTrue(audit(self.sc,r,ledger)['coverage_review_complete'])
    def test_stale_ledger_hash_blocked(self):
        ledger=self.ledger();ledger['current_sha256']='0'*64
        self.assertIn('LEDGER_SCRIPT_HASH_MISMATCH',audit(self.sc,self.review(),ledger)['errors'])
    def test_no_ledger_backward_compatible(self):
        self.assertTrue(audit(self.sc,self.review())['coverage_review_complete'])
    def test_script_change(self):
        original=self.sc['script_sha256'];self.path.write_text(SCRIPT+'△又找到照片。\n',encoding='utf-8')
        self.assertNotEqual(original,scan(self.path)['script_sha256'])

if __name__=='__main__':unittest.main()
