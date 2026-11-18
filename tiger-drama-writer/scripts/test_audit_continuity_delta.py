import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from audit_continuity_delta import audit

class ContinuityTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.a=root/'one.md';self.b=root/'two.md';self.l=root/'ledger.json'
        self.p='### SC01\n△阿遥左手打着石膏，戒指装在口袋里。\n'
        self.c='### SC01\n△医生拆下阿遥左手的石膏，她拿出戒指。\n'
        self.a.write_text(self.p,encoding='utf-8');self.b.write_text(self.c,encoding='utf-8')
        self.d={'previous_sha256':hashlib.sha256(self.a.read_bytes()).hexdigest(),
            'current_sha256':hashlib.sha256(self.b.read_bytes()).hexdigest(),
            'previous_state':{'阿遥.左手':'石膏固定'}, 'current_state':{'阿遥.左手':'石膏拆除'},
            'previous_anchors':{'阿遥.左手':'阿遥左手打着石膏，戒指装在口袋里'},
            'changes':[{'key':'阿遥.左手','from':'石膏固定','to':'石膏拆除',
                'current_quote':'医生拆下阿遥左手的石膏，她拿出戒指', 'interpretation':'本场明确展示医生拆除石膏这一变化'}]}
    def check(self):
        self.l.write_text(json.dumps(self.d,ensure_ascii=False),encoding='utf-8')
        return audit(self.a,self.b,self.l)
    def test_valid(self):self.assertTrue(self.check()['mechanically_valid'])
    def test_missing_change(self):
        self.d['changes']=[]
        self.assertIn('UNEXPLAINED_STATE_CHANGE_阿遥.左手',self.check()['errors'])
    def test_fake_quote(self):
        self.d['changes'][0]['current_quote']='不存在的医生将石膏轻轻拆掉了'
        self.assertFalse(self.check()['mechanically_valid'])
    def test_stale_hash(self):
        self.b.write_text(self.c+'△新增动作。',encoding='utf-8')
        self.assertIn('CURRENT_SHA256_MISMATCH',self.check()['errors'])
    def test_duplicate_change(self):
        self.d['changes'].append(dict(self.d['changes'][0]))
        self.assertFalse(self.check()['mechanically_valid'])
    def test_missing_previous_anchor(self):
        self.d['previous_anchors']={}
        self.assertFalse(self.check()['mechanically_valid'])

    def test_new_key_requires_registration(self):
        self.d['current_state']['阿遥.戒指']='手中'
        self.assertIn('UNREGISTERED_NEW_KEY_阿遥.戒指',self.check()['errors'])
    def test_new_key_with_quote_passes(self):
        self.d['current_state']['阿遥.戒指']='手中'
        self.d['introduced']=[{'key':'阿遥.戒指','value':'手中',
            'current_quote':'她拿出戒指', 'interpretation':'该集开始正式追踪人物手里的戒指'}]
        # Quote intentionally too short, must be rejected.
        self.assertIn('INTRODUCTION_QUOTE_NOT_UNIQUE_阿遥.戒指',self.check()['errors'])
        self.d['introduced'][0]['current_quote']='医生拆下阿遥左手的石膏，她拿出戒指'
        self.assertTrue(any(x.startswith('CURRENT_EVIDENCE_REUSED_WITHOUT_REASON_') for x in self.check()['errors']))
        self.d['changes'][0]['shared_evidence_reason']='同一动作同时展示了拆除石膏及取出戒指，两个状态分别都有明确来源。'
        self.d['introduced'][0]['shared_evidence_reason']='同一动作同时展示了拆除石膏及取出戒指，两个状态分别都有明确来源。'
        self.assertTrue(self.check()['mechanically_valid'])
    def test_duplicate_introduction_fails(self):
        self.d['current_state']['阿遥.戒指']='手中'
        item={'key':'阿遥.戒指','value':'手中','current_quote':'医生拆下阿遥左手的石膏，她拿出戒指','interpretation':'该集开始正式追踪戒指的持有人'}
        self.d['introduced']=[item,item.copy()]
        self.assertIn('DUPLICATE_INTRODUCTION_阿遥.戒指',self.check()['errors'])
    def test_dropped_key_fails(self):
        self.d['current_state']={}
        self.assertIn('DROPPED_TRACKED_KEY_阿遥.左手',self.check()['errors'])
    def test_empty_ledger_fails(self):
        self.d.update(previous_state={},current_state={},previous_anchors={},changes=[])
        self.assertIn('EMPTY_STATE_MAP',self.check()['errors'])
    def test_invalid_intro_value_fails(self):
        self.d['current_state']['阿遥.戒指']='手中'
        self.d['introduced']=[{'key':'阿遥.戒指','value':'遗失','current_quote':'医生拆下阿遥左手的石膏，她拿出戒指','interpretation':'本集新增的戒指追踪状态与正文一致'}]
        self.assertIn('INTRODUCTION_VALUE_MISMATCH_阿遥.戒指',self.check()['errors'])

if __name__=='__main__':unittest.main()
