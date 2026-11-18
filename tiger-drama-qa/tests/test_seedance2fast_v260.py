from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_seedance2fast_v260_independent import review

FIX=ROOT/'tests'/'fixtures-v260'
EXPECTED=','.join('SH%02d'%i for i in range(1,6))
class TestV260QA(unittest.TestCase):
    def test_all_six(self):
        docs=sorted(FIX.glob('05-Seedance2Fast-0*.md'))
        self.assertEqual(len(docs),6)
        for p in docs:
            with self.subTest(p.name):
                r=review(p,EXPECTED)
                self.assertFalse(r['issues'],r)

    def break_text(self,a,b):
        source=next(FIX.glob('05-Seedance2Fast-06-*.md')).read_text(encoding='utf-8')
        self.assertIn(a,source)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.md';p.write_text(source.replace(a,b,1),encoding='utf-8')
            return review(p,EXPECTED)
    def test_missing_key_picture(self):
        r=self.break_text('【00:08.0｜SH05｜关键画面】','【00:08.0｜SH05｜其他】')
        self.assertTrue(r['issues'])
    def test_trimmed_key_picture(self):
        r=self.break_text('【00:08.0｜SH05｜关键画面】','【00:09.0｜SH05｜关键画面】')
        self.assertTrue(any('CUT-OFF' in x for x in r['issues']))
    def test_wrong_shot(self):
        r=self.break_text('【00:08.0｜SH05｜关键画面】','【00:08.0｜SH02｜关键画面】')
        self.assertTrue(any('WRONG-CUE' in x for x in r['issues']))
    def test_absolute_film_position_gap(self):
        r=self.break_text('**成片位置**：00:06.5-00:15.0','**成片位置**：00:06.7-00:15.0')
        self.assertTrue(any('Q-ABSOLUTE' in x for x in r['issues']))

    def test_duplicate_milestone(self):
        s='【00:08.0｜SH05｜关键画面】极远景中同一整道山脉成为巨龙身躯，固定龙眼清晰且与最初山势一致。'
        r=self.break_text(s,s+'\n'+s)
        self.assertTrue(r['issues'])

if __name__=='__main__':unittest.main()
