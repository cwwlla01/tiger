import sys,unittest,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from serial_pipeline import run

class SerialPipelineTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
    def tearDown(self):self.t.cleanup()
    def manifest(self,items):
        p=self.root/'manifest.json';p.write_text(json.dumps({'episodes':items}),encoding='utf-8');return p
    def test_empty(self):self.assertEqual(run(self.manifest([]))['status'],'INVALID_MANIFEST')
    def test_wrong_order(self):self.assertEqual(run(self.manifest([{'number':2,'file':'x.md'}]))['status'],'BLOCKED_ORDER')
    def test_missing_file(self):self.assertEqual(run(self.manifest([{'number':1,'file':'missing.md'}]))['status'],'BLOCKED_MISSING_FILE')
    def test_stops_at_first_failed_episode(self):
        (self.root/'EP01.md').write_text('## EP01\n### 场1\n人物：你好',encoding='utf-8')
        self.assertEqual(run(self.manifest([{'number':1,'file':'EP01.md'},{'number':2,'file':'EP02.md'}]))['status'],'BLOCKED_STATIC')
        self.assertEqual(len(run(self.root/'manifest.json')['history']),1)
    def test_no_editorial_autopass(self):
        # Stub authorization, preserving real orchestration semantics.
        from unittest.mock import patch
        (self.root/'a.md').write_text('## EP01',encoding='utf-8')
        with patch('serial_pipeline.check',return_value={'sha256':'a','issues':[],'static_ready_for_editorial_review':True}):
            self.assertEqual(run(self.manifest([{'number':1,'file':'a.md'}]))['status'],'BLOCKED_EDITORIAL')
    def test_review_denied_stops(self):
        from unittest.mock import patch
        (self.root/'a.md').write_text('## EP01',encoding='utf-8')
        (self.root/'r.json').write_text('{}',encoding='utf-8')
        with patch('serial_pipeline.check',return_value={'sha256':'a','issues':[],'static_ready_for_editorial_review':True}),patch('serial_pipeline.authorize',return_value={'issues':['EDITORIAL_NOT_APPROVED'],'next_episode_authorized':False}):
            self.assertEqual(run(self.manifest([{'number':1,'file':'a.md','review':'r.json'}]))['status'],'BLOCKED_EDITORIAL')
if __name__=='__main__':unittest.main()
