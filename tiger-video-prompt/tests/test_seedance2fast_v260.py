from __future__ import annotations
import unittest
import tempfile
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_seedance2fast_v260 import audit

FIX=ROOT/'tests'/'fixtures-v260'
EXPECTED=','.join(f'SH{i:02d}' for i in range(1,6))

class TestV260(unittest.TestCase):
    def test_all_six(self):
        docs=sorted(FIX.glob('05-Seedance2Fast-0*.md'))
        self.assertEqual(len(docs),6)
        for file in docs:
            with self.subTest(file=file.name):
                result=audit(file,EXPECTED)
                self.assertEqual(result['status'],'TEXT_STRUCTURE_PASS',result['errors'])
                self.assertEqual(len(result['visible_payoff_checks']),4 if '-04-' in file.name else 5)

    def changed(self,replacements):
        source=next(FIX.glob('05-Seedance2Fast-06-*.md')).read_text(encoding='utf-8')
        for a,b in replacements:
            self.assertIn(a,source)
            source=source.replace(a,b,1)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'sample.md';path.write_text(source,encoding='utf-8')
            return audit(path,EXPECTED)

    def test_missing_payoff(self):
        r=self.changed([('【00:08.0｜SH05｜关键画面】','【关键画面】')])
        self.assertTrue(any('PAYOFF' in e for e in r['errors']))

    def test_payoff_trimmed_but_shot_overlap(self):
        r=self.changed([('【00:08.0｜SH05｜关键画面】','【00:09.1｜SH05｜关键画面】')])
        self.assertTrue(any('E-PAYOFF-TRIMMED' in e for e in r['errors']))

    def test_payoff_wrong_shot(self):
        r=self.changed([('【00:08.0｜SH05｜关键画面】','【00:08.0｜SH03｜关键画面】')])
        self.assertTrue(any('E-PAYOFF-ID' in e for e in r['errors']))

    def test_payoff_outside_shot(self):
        r=self.changed([('【00:08.0｜SH05｜关键画面】','【00:05.0｜SH05｜关键画面】')])
        self.assertTrue(any('E-PAYOFF-OUTSIDE-SHOT' in e for e in r['errors']))

    def test_duplicate_payoff(self):
        line='【00:08.0｜SH05｜关键画面】极远景中同一整道山脉成为巨龙身躯，固定龙眼清晰且与最初山势一致。'
        r=self.changed([(line,line+'\n'+line)])
        self.assertTrue(any('E-PAYOFF' in e for e in r['errors']))

    def test_trim_end_barely_contains(self):
        r=self.changed([('【00:08.0｜SH05｜关键画面】','【00:08.49｜SH05｜关键画面】')])
        self.assertTrue(any('E-PAYOFF-TRIMMED' in e for e in r['errors']))

    def test_generator_time_mismatch(self):
        r=self.changed([('**生成时长**：10秒','**生成时长**：7秒')])
        self.assertTrue(any('E-' in e for e in r['errors']))

    def test_absolute_film_position_gap(self):
        r=self.changed([('**成片位置**：00:06.5-00:15.0','**成片位置**：00:06.7-00:15.0')])
        self.assertTrue(any('E-FILM-GAP' in e or 'E-FILM-SPAN' in e for e in r['errors']))

    def test_missing_world_light(self):
        r=self.changed([('光线总规则：','照明设定：')])
        self.assertTrue(any('E-GLOBAL' in e for e in r['errors']))

if __name__=='__main__':unittest.main()
