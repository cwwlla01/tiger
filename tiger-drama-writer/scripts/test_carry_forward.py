import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_continuity_delta import audit
import hashlib

class CarryForwardTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.a=self.root/'a.md'; self.b=self.root/'b.md'; self.ledger=self.root/'ledger.json'
        self.a.write_text('第二集里他们讨论了其他问题，未提钥匙的所在。',encoding='utf-8')
        self.source=self.root/'source.md'
        self.source.write_text('△女孩明确把旧钥匙放进自己的口袋，不让别人接触。',encoding='utf-8')
        self.b.write_text('△女孩把旧钥匙交给了警方，并拿走收据。',encoding='utf-8')
        self.payload={'previous_sha256':hashlib.sha256(self.a.read_bytes()).hexdigest(),'current_sha256':hashlib.sha256(self.b.read_bytes()).hexdigest(), 'previous_state':{'钥匙':'仍由女孩持有'},'current_state':{'钥匙':'已经交给警方'},'changes':[{'key':'钥匙','from':'仍由女孩持有','to':'已经交给警方','current_quote':'△女孩把旧钥匙交给了警方，并拿走收据。','interpretation':'本集发生一次明确的物品移交，双方位置和状态已变化'}],'introduced':[],'previous_anchors':{'钥匙':{'kind':'carry_forward','editor_reviewed':True,'review_reason':'上一集没有重复描述该钥匙，编辑已按此前状态核对并确认没有移交','source_script':'source.md','source_sha256':hashlib.sha256(self.source.read_bytes()).hexdigest(),'source_quote':'△女孩明确把旧钥匙放进自己的口袋，不让别人接触。'}}}
    def check(self):
        self.ledger.write_text(json.dumps(self.payload,ensure_ascii=False),encoding='utf-8');return audit(self.a,self.b,self.ledger)
    def test_editor_attested_carry(self):self.assertTrue(self.check()['mechanically_valid'])
    def test_absent_review(self):
        self.payload['previous_anchors']['钥匙']['editor_reviewed']=False
        self.assertIn('CARRY_FORWARD_REVIEW_REQUIRED_钥匙',self.check()['errors'])
    def test_short_reason(self):
        self.payload['previous_anchors']['钥匙']['review_reason']='OK'
        self.assertIn('CARRY_FORWARD_REASON_REQUIRED_钥匙',self.check()['errors'])
    def test_missing_source_rejected(self):
        del self.payload['previous_anchors']['钥匙']['source_script']
        self.assertIn('CARRY_SOURCE_REQUIRED_钥匙',self.check()['errors'])
    def test_wrong_source_hash_rejected(self):
        self.payload['previous_anchors']['钥匙']['source_sha256']='0'*64
        self.assertIn('CARRY_SOURCE_SHA256_MISMATCH_钥匙',self.check()['errors'])
    def test_nonexistent_source_quote_rejected(self):
        self.payload['previous_anchors']['钥匙']['source_quote']='一段根本不存在的剧本台词和动作'
        self.assertIn('CARRY_SOURCE_QUOTE_NOT_UNIQUE_钥匙',self.check()['errors'])
    def test_source_file_missing_rejected(self):
        self.payload['previous_anchors']['钥匙']['source_script']='missing.md'
        self.assertIn('CARRY_SOURCE_UNREADABLE_钥匙',self.check()['errors'])
    def test_forged_quote_still_fails(self):
        self.payload['previous_anchors']['钥匙']='前一集不存在的物品移交情节'
        self.assertIn('PREVIOUS_ANCHOR_NOT_UNIQUE_钥匙',self.check()['errors'])
if __name__=='__main__':unittest.main()
