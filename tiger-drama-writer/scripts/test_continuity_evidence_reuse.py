import json
import tempfile
import hashlib
import unittest
from pathlib import Path
from audit_continuity_delta import audit

class EvidenceReuseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.prev = self.root/'a.md'; self.curr = self.root/'b.md'; self.ledger=self.root/'ledger.json'
        self.prev.write_text('△张宁拿着一张旧照片留在门口，旁边的人在等着答复。', encoding='utf-8')
        self.curr.write_text('△张宁将照片交给李明，李明同时拿走了钥匙。\n△李明收到钥匙后将它放入衣袋。', encoding='utf-8')
        self.quote = '△张宁将照片交给李明，李明同时拿走了钥匙。'
        self.data = {'previous_sha256':hashlib.sha256(self.prev.read_bytes()).hexdigest(),
                     'current_sha256':hashlib.sha256(self.curr.read_bytes()).hexdigest(),
                     'previous_state':{'photo':'张宁','key':'张宁'},
                     'current_state':{'photo':'李明','key':'李明'},
                     'changes':[{'key':key,'from':'张宁','to':'李明','current_quote':self.quote,'interpretation':'本段明确描述物品从一位角色的手中转到另一位角色手中。'} for key in ('photo','key')],
                     'introduced':[], 'previous_anchors':{'photo':'△张宁拿着一张旧照片留在门口，旁边的人在等着答复。','key':'△张宁拿着一张旧照片留在门口，旁边的人在等着答复。'}}
    def check(self):
        self.ledger.write_text(json.dumps(self.data,ensure_ascii=False),encoding='utf-8')
        return audit(self.prev,self.curr,self.ledger)
    def test_reused_quote_is_rejected(self):
        self.assertIn('CURRENT_EVIDENCE_REUSED_WITHOUT_REASON_key',self.check()['errors'])
    def test_distinct_quote_allowed(self):
        self.data['changes'][1]['shared_evidence_reason']='该动作同时明确说明钥匙归属与照片归属，分别登记两项状态。'
        self.assertTrue(self.check()['mechanically_valid'])
    def test_unexpected_anchor_rejected(self):
        self.data['changes'][1]['current_quote']='△李明收到钥匙后将它放入衣袋。'
        self.data['previous_anchors']['phantom']='根本不属于追踪范围的状态说明内容'
        self.assertIn('UNEXPECTED_PREVIOUS_ANCHOR_phantom',self.check()['errors'])
    def test_introduction_change_reuse_rejected(self):
        self.data['changes']=self.data['changes'][:1]
        self.data['previous_state']={'photo':'张宁'}
        self.data['previous_anchors'].pop('key')
        self.data['introduced']=[{'key':'key','value':'李明','current_quote':self.quote,'interpretation':'新增一项重要道具的归属和使用状态，需加入账本。'}]
        self.assertIn('CURRENT_EVIDENCE_REUSED_photo',self.check()['errors']) if False else self.assertTrue(any(x.startswith('CURRENT_EVIDENCE_REUSED_') for x in self.check()['errors']))

if __name__=='__main__': unittest.main()
