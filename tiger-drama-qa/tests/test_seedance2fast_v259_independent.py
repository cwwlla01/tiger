#!/usr/bin/env python3
"""V2.59 second implementation source/time/POST regression tests."""
import importlib.util, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SPEC=importlib.util.spec_from_file_location('qa_v259',ROOT/'scripts'/'audit_seedance2fast_v259_independent.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)
FILES=sorted((HERE/'fixtures-v259').glob('05-Seedance2Fast-0*.md'))
assert len(FILES)==6
BASE={f.name.split('-')[2]:f.read_text(encoding='utf-8') for f in FILES}
SRC='SH01,SH02,SH03,SH04,SH05'
class TestQA(unittest.TestCase):
    def check(self,s,code=None):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'candidate.md';p.write_text(s,encoding='utf-8')
            out=A.review(p,SRC)
            if code:
                self.assertEqual(out['status'],'INDEPENDENT_STRUCTURE_FAIL')
                self.assertTrue(any(code in x for x in out['issues']),out)
            else:self.assertEqual(out['status'],'INDEPENDENT_STRUCTURE_PASS',out)
    def test_all_six(self):
        for f in FILES:
            with self.subTest(f=f.name):self.check(f.read_text(encoding='utf-8'))
    def test_wrong_inline_sh(self):self.check(BASE['06'].replace('｜SH02｜镜头2','｜SH03｜镜头2',1),'Q-SHOT-MAP')
    def test_bad_keep(self):self.check(BASE['06'].replace('**剪辑截取**：00:00.0-00:06.5','**剪辑截取**：00:00.0-00:08.5',1),'Q-KEEP-REGION')
    def test_bad_post(self):self.check(BASE['04'].replace('**剪辑时长**：1秒','**剪辑时长**：2秒'),'Q-FINAL-TIME')
    def test_post_not_video(self):self.check(BASE['04'].replace('## POST01｜','## POST01｜\n```text\n黑场\n```\n',1),'Q-POST-FORMAT')
    def test_missing_sound(self):self.check(BASE['04'].replace('**声画规则**','**其他规则**'),'Q-POST-EVIDENCE')
    def test_missing_cut(self):self.check(BASE['02'].replace('硬切。摄影机：','镜头转换。摄影机：',1),'Q-CUT')
    def test_missing_light(self):self.check(BASE['06'].replace('光线：左侧夕阳勾勒','受光：左侧夕阳勾勒',1),'Q-PER-SHOT-光线：')
    def test_missing_post(self):
        a=BASE['04'].index('## POST01');b=BASE['04'].index('## T02',a)
        self.check(BASE['04'][:a]+BASE['04'][b:],'Q-SOURCE-COVERAGE')
    def test_dropped_trimmed_shot(self):
        x=BASE['06'].replace('**剪辑保留**：6.5秒','**剪辑保留**：2秒',1).replace('**剪辑截取**：00:00.0-00:06.5','**剪辑截取**：00:00.0-00:02.0',1)
        self.check(x,'Q-EDIT-COVERAGE')
    def test_forged_media(self):self.check(BASE['06'].replace('【终态】','@图片1【终态】',1),'Q-UNVERIFIED-INPUT')
if __name__=='__main__':unittest.main()
