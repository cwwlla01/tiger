import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from editorial_authorize import authorize,CATEGORIES

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.source=Path(self.tmp.name)/'EP01.md';self.source.write_text('## EP01《试片》\n乙拦住大门，甲立刻改走消防通道。\n甲将唯一的钥匙交给乙，门从此无法反锁。\n乙终于公开道歉，甲却决定离开。\n水剩下一桶，甲右臂受伤。',encoding='utf-8')
        lines=self.source.read_text().splitlines()
        quotes=[lines[1],lines[2],lines[3],lines[4]]
        self.review={'episode':1,'sha256':hashlib.sha256(self.source.read_bytes()).hexdigest(),'reviewer':'人工编辑A','editorial_decision':'approved','evidence':{c:{'assessment':'已人工核对','quote':q} for c,q in zip(CATEGORIES,quotes)}}
        self.record=Path(self.tmp.name)/'review.json';self.save()
    def save(self):self.record.write_text(json.dumps(self.review,ensure_ascii=False),encoding='utf-8')
    def run_gate(self):
        with patch('editorial_authorize.check',return_value={'issues':[],'static_ready_for_editorial_review':True}):return authorize(self.source,1,self.record)
    def test_valid_review(self):self.assertTrue(self.run_gate()['next_episode_authorized'])
    def test_modified_source_invalidates_review(self):
        self.source.write_text(self.source.read_text()+'补写',encoding='utf-8')
        self.assertIn('SOURCE_HASH_MISMATCH',self.run_gate()['issues'])
    def test_other_episode_quote_rejected(self):
        self.review['evidence']['irreversible_change']['quote']='另一个剧集发生的重大变化';self.save()
        self.assertIn('UNSUPPORTED_IRREVERSIBLE_CHANGE',self.run_gate()['issues'])
    def test_missing_category_rejected(self):
        del self.review['evidence']['continuity_delta'];self.save()
        self.assertIn('MISSING_CONTINUITY_DELTA',self.run_gate()['issues'])
    def test_unapproved_rejected(self):
        self.review['editorial_decision']='rejected';self.save()
        self.assertIn('EDITORIAL_NOT_APPROVED',self.run_gate()['issues'])
    def test_static_failure_rejected(self):
        with patch('editorial_authorize.check',return_value={'issues':['THIN_SCENE'],'static_ready_for_editorial_review':False}):
            self.assertFalse(authorize(self.source,1,self.record)['next_episode_authorized'])
if __name__=='__main__':unittest.main()
