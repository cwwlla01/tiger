#!/usr/bin/env python3
"""Regression tests for V2.59 production gate; all fixtures are bundled."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SPEC=importlib.util.spec_from_file_location('audit_v259', ROOT/'scripts'/'audit_seedance2fast_v259.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)
FILES=sorted((HERE/'fixtures-v259').glob('05-Seedance2Fast-0*.md'))
assert len(FILES)==6
BASE={f.name.split('-')[2]:f.read_text(encoding='utf-8') for f in FILES}
IDS=','.join(f'SH{i:02d}' for i in range(1,6))

class TestGate(unittest.TestCase):
    def check(self,txt,err=None):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.md';p.write_text(txt,encoding='utf-8')
            r=A.audit(p,IDS)
            if err:
                self.assertEqual('TEXT_STRUCTURE_FAIL',r['status'],r)
                self.assertTrue(any(err in x for x in r['errors']),r)
            else:
                self.assertEqual('TEXT_STRUCTURE_PASS',r['status'],r)
            return r
    def test_six_cases_pass(self):
        for f in FILES:
            with self.subTest(f=f.name): self.check(f.read_text(encoding='utf-8'))
    def test_first_scene_3_takes_5_shots(self):
        x=self.check(BASE['01']);self.assertEqual(x['stats']['take_count'],3)
        self.assertEqual(x['stats']['shot_count'],5)
    def test_door_single_take_5_shots(self):
        x=self.check(BASE['02']);self.assertEqual(x['stats']['take_count'],1)
    def test_surgery_has_true_post_only(self):
        x=self.check(BASE['04']);self.assertEqual(x['stats']['post_seconds'],1)
        self.assertEqual(x['stats']['retained_seconds'],14)
    def test_time_shot_id_missing(self):
        self.check(BASE['06'].replace('｜SH02｜镜头2','｜镜头2',1),'E-SHOT-SPAN-MAP')
    def test_time_shot_id_wrong(self):
        self.check(BASE['06'].replace('｜SH02｜镜头2','｜SH03｜镜头2',1),'E-SHOT-SPAN-MAP')
    def test_keep_range_missing(self):
        self.check(BASE['02'].replace('**剪辑截取**','**剪辑意向**'),'E-KEEP-RANGE')
    def test_keep_range_disagrees(self):
        self.check(BASE['06'].replace('**剪辑截取**：00:00.0-00:06.5','**剪辑截取**：00:00.0-00:06.0',1),'E-KEEP-MISMATCH')
    def test_trimmed_shot_silently_lost(self):
        x=BASE['06'].replace('**剪辑保留**：6.5秒','**剪辑保留**：2秒',1).replace('**剪辑截取**：00:00.0-00:06.5','**剪辑截取**：00:00.0-00:02.0',1)
        x=x.replace('**剪辑总时长**：15秒','**剪辑总时长**：10.5秒',1)
        self.check(x,'E-KEEP-DROPS-SHOT')
    def test_post_missing_from_source(self):
        x=BASE['04'];a=x.index('## POST01');b=x.index('## T02',a)
        self.check(x[:a]+x[b:],'E-SOURCE-COVERAGE')
    def test_post_duration_wrong(self):
        self.check(BASE['04'].replace('**剪辑时长**：1秒','**剪辑时长**：2秒'),'E-SCENE-SUM')
    def test_post_as_video_code(self):
        self.check(BASE['04'].replace('## POST01｜灯灭黑场（纯后期）','## POST01｜灯灭黑场（纯后期）\n\n```text\n请生成黑色视频\n```'),'E-POST-CODE')
    def test_post_missing_sound(self):
        self.check(BASE['04'].replace('**声画规则**','**其他规则**'),'E-POST-BRIEF')
    def test_missing_cut(self):
        self.check(BASE['06'].replace('硬切。摄影机：','镜头转换。摄影机：',1),'E-CUT')
    def test_missing_camera(self):
        self.check(BASE['05'].replace('摄影机：35mm','机位：35mm',1),'E-FIELD')
    def test_missing_lighting(self):
        self.check(BASE['01'].replace('光线：左前上方阴冷天光','受光：左前上方阴冷天光',1),'E-FIELD')
    def test_missing_sound(self):
        self.check(BASE['03'].replace('声音：伞面雨点连续敲击','环境声：伞面雨点连续敲击',1),'E-FIELD')
    def test_low_generate_duration(self):
        self.check(BASE['06'].replace('**生成时长**：8秒','**生成时长**：3秒',1),'E-GEN')
    def test_gap(self):
        self.check(BASE['06'].replace('【00:03.5-00:08.0｜SH02','【00:03.7-00:08.0｜SH02'),'E-TIME-GAP')
    def test_tail(self):
        self.check(BASE['06'].replace('【00:03.5-00:08.0｜SH02','【00:03.5-00:07.0｜SH02'),'E-TIME-END')
    def test_missing_model(self):
        self.check(BASE['06'].replace('**模型**：Seedance 2 Fast','**模型**：其他'),'E-MODEL')
    def test_missing_global(self):
        self.check(BASE['06'].replace('【终态】','【结果】',1),'E-GLOBAL')
    def test_fake_media_ref(self):
        self.check(BASE['06'].replace('【终态】','@图片1【终态】',1),'E-FAKE-REF')
    def test_management_in_copy_block(self):
        self.check(BASE['06'].replace('【终态】','PLACEHOLDER【终态】',1),'E-MGMT')
    def test_source_reorder(self):
        self.check(BASE['06'].replace('**编辑镜头**：SH03、SH04、SH05','**编辑镜头**：SH03、SH05、SH04',1),'E-SHOT-SPAN-MAP')
    def test_duplicate_take(self):
        self.check(BASE['06'].replace('## T02｜龙眼与尺度反转','## T01｜龙眼与尺度反转'),'E-UNIT-DUP')
    def test_without_source_ids_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.md';p.write_text(BASE['06'],encoding='utf-8')
            self.assertTrue(any('E-SOURCE' in x for x in A.audit(p,None)['errors']))

if __name__=='__main__':unittest.main()
