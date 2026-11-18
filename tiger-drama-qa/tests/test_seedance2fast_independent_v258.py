#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve()
SPEC=importlib.util.spec_from_file_location('independent_qa',HERE.parents[1]/'scripts'/'audit_seedance2fast_independent.py')
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
ORIGINAL=(HERE.parent/'fixtures'/'05-Seedance2Fast-山后巨龙-文本候选.md').read_text(encoding='utf8')
EXPECTED='SH01,SH02,SH03,SH04,SH05'

class TestIndependentQA(unittest.TestCase):
    def test_pass(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'05.md';p.write_text(ORIGINAL,encoding='utf8')
            self.assertEqual('INDEPENDENT_STRUCTURE_PASS',mod.audit(p,EXPECTED)['status'])
    def test_missing_source_shot(self):
        changed=ORIGINAL.replace('SH03、SH04、SH05','SH03、SH05')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'05.md';p.write_text(changed,encoding='utf8')
            self.assertTrue(any('Q-SOURCE-COVERAGE' in e for e in mod.audit(p,EXPECTED)['errors']))
    def test_reordered_source_shot(self):
        changed=ORIGINAL.replace('SH03、SH04、SH05','SH05、SH04、SH03')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'05.md';p.write_text(changed,encoding='utf8')
            self.assertTrue(any('Q-SOURCE-COVERAGE' in e for e in mod.audit(p,EXPECTED)['errors']))
    def test_missing_lighting(self):
        changed=ORIGINAL.replace('光线：仍由世界空间左侧夕阳','受光表现：仍由世界空间左侧夕阳')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'05.md';p.write_text(changed,encoding='utf8')
            self.assertTrue(any('Q-PER-SHOT-FIELD' in e for e in mod.audit(p,EXPECTED)['errors']))
    def test_no_source_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'05.md';p.write_text(ORIGINAL,encoding='utf8')
            self.assertTrue(any('Q-NO-SOURCE' in e for e in mod.audit(p,'')['errors']))

if __name__=='__main__': unittest.main()
