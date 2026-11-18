import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from audit_continuity_chain import check_chain

BASE = Path(__file__).parent / 'fixtures' / 'continuity_five'

class ChainOriginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        for p in BASE.glob('EP0[1-5].md'):
            (self.dir / p.name).write_bytes(p.read_bytes())
        for p in BASE.glob('L0[1-4]_0[2-5].json'):
            (self.dir / p.name).write_bytes(p.read_bytes())
        self.entries = [{'previous_script':str(self.dir/f'EP{i:02}.md'), 'current_script':str(self.dir/f'EP{i+1:02}.md'),'ledger':str(self.dir/f'L{i:02}_0{i+1}.json')} for i in range(1,5)]
    def test_real_five_episode_chain(self):
        self.assertTrue(check_chain(self.entries)['mechanically_valid'])
    def test_stale_source_after_intervening_change(self):
        source=(self.dir/'EP01.md').read_text()
        quote=next(line.strip() for line in source.splitlines() if len(line.strip())>15 and source.count(line.strip())==1)
        ledger_path=self.dir/'L03_04.json'
        d=json.loads(ledger_path.read_text())
        a=d['previous_anchors']['少年.姓名信息']
        a.update(source_script='EP01.md',source_sha256=hashlib.sha256((self.dir/'EP01.md').read_bytes()).hexdigest(), source_quote=quote)
        ledger_path.write_text(json.dumps(d,ensure_ascii=False))
        r=check_chain(self.entries)
        self.assertIn('CARRY_SOURCE_STALE_AFTER_CHANGE_2_少年.姓名信息',r['errors'])
    def test_outside_chain_source(self):
        outsider=self.dir/'old_draft.md'
        outsider.write_text('独立的无关前稿文本，仅供引用。' * 3)
        ledger_path=self.dir/'L03_04.json'
        d=json.loads(ledger_path.read_text())
        a=d['previous_anchors']['少年.姓名信息']
        a.update(source_script='old_draft.md',source_sha256=hashlib.sha256(outsider.read_bytes()).hexdigest(),source_quote='独立的无关前稿文本，仅供引用。')
        ledger_path.write_text(json.dumps(d,ensure_ascii=False))
        self.assertIn('CARRY_SOURCE_OUTSIDE_CHAIN_2_少年.姓名信息',check_chain(self.entries)['errors'])

if __name__=='__main__': unittest.main()
