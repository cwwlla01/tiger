#!/usr/bin/env python3
"""Run: python -m unittest discover -s tests -p 'test_seedance2fast_v258.py' -v"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve()
SKILL_ROOT=HERE.parents[1]
EXAMPLE=HERE.parent/'fixtures'/'05-Seedance2Fast-山后巨龙-文本候选.md'
SPEC=importlib.util.spec_from_file_location('audit_v258',SKILL_ROOT/'scripts'/'audit_seedance2fast_delivery.py')
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
ORIGINAL=EXAMPLE.read_text(encoding='utf8')
IDS='SH01,SH02,SH03,SH04,SH05'


class TestSeedance2FastGate(unittest.TestCase):
    def check(self, text, want):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'05.md';f.write_text(text,encoding='utf8')
            result=MODULE.audit(f,IDS)
            if want == 'PASS':
                self.assertEqual('TEXT_STRUCTURE_PASS',result['status'], result['errors'])
            else:
                self.assertEqual('TEXT_STRUCTURE_FAIL',result['status'])
                self.assertTrue(any(want in x for x in result['errors']),result['errors'])
    def test_good_two_takes_five_shots(self): self.check(ORIGINAL,'PASS')
    def test_missing_timeline(self): self.check(ORIGINAL.replace('【00:03.5-00:08.0｜镜头2】','镜头2：'),'E-SHOT-COUNT')
    def test_timeline_gap(self): self.check(ORIGINAL.replace('【00:03.5-00:08.0｜镜头2】','【00:04.0-00:08.0｜镜头2】'),'E-TIMELINE-GAP')
    def test_timeline_tail(self): self.check(ORIGINAL.replace('【00:03.5-00:08.0｜镜头2】','【00:03.5-00:07.5｜镜头2】'),'E-TIMELINE-TAIL')
    def test_missing_cut(self): self.check(ORIGINAL.replace('】硬切。摄影机：100mm','】镜头转换。摄影机：100mm'),'E-CUT')
    def test_missing_camera(self): self.check(ORIGINAL.replace('摄影机：100mm长焦中远景','摄影说明：100mm长焦中远景'),'E-CAMERA')
    def test_missing_lighting(self): self.check(ORIGINAL.replace('光线：仍由世界空间左侧夕阳','受光：仍由世界空间左侧夕阳'),'E-LIGHT')
    def test_missing_sound(self): self.check(ORIGINAL.replace('声音：持续深沉岩层挤压声','声场：持续深沉岩层挤压声'),'E-SOUND')
    def test_empty_action(self): self.check(ORIGINAL.replace('动作：山脊局部缓缓向上抬升，','动作：，'),'E-ACTION-EMPTY')
    def test_false_image_binding(self): self.check(ORIGINAL.replace('【禁改】','@图片1【禁改】',1),'E-UNVERIFIED-AT-REF')
    def test_retained_over_generated(self): self.check(ORIGINAL.replace('**剪辑保留**：6.5秒','**剪辑保留**：9秒'),'E-RETAIN-RANGE')
    def test_model_duration_over_15(self): self.check(ORIGINAL.replace('**生成时长**：8秒','**生成时长**：16秒'),'E-MODEL-RANGE')
    def test_source_missing(self): self.check(ORIGINAL.replace('**编辑镜头**：SH01、SH02','**编辑镜头**：SH01'),'E-SOURCE-MISSING')
    def test_source_reordered(self): self.check(ORIGINAL.replace('**编辑镜头**：SH03、SH04、SH05','**编辑镜头**：SH03、SH05、SH04'),'E-SOURCE-ORDER')
    def test_missing_merge_rationale(self): self.check(ORIGINAL.replace('**合并决策**','**导演备注**',1),'E-MERGE-DECISION')
    def test_missing_final_state(self): self.check(ORIGINAL.replace('【终态】山脊','【后记】山脊'),'E-GLOBAL')
    def test_false_ready_management_text(self): self.check(ORIGINAL.replace('【终态】','PLACEHOLDER【终态】',1),'E-MANAGEMENT-TEXT')
    def test_duplicate_take_id(self): self.check(ORIGINAL.replace('## T02｜巨龙苏醒','## T01｜巨龙苏醒'),'E-TAKE-DUPLICATE')
    def test_missing_source_arg_fails(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'05.md'; f.write_text(ORIGINAL,encoding='utf8')
            r=MODULE.audit(f,None)
            self.assertTrue(any('E-NO-SOURCE' in s for s in r['errors']))

if __name__=='__main__': unittest.main()
