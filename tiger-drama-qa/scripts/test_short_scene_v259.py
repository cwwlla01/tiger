import unittest
from pathlib import Path
class TestShortSceneV259(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(sum((4,3,5,3)),15)
    def test_director_contract(self):
        p=Path(__file__).resolve().parents[1]/'references/short-scene-creative-audit-v259.md'
        self.assertIn('NOT_VERIFIED',p.read_text(encoding='utf-8'))
    def test_fixture_source(self):
        p=Path(__file__).resolve().parent/'fixtures/short_scene_v259/REVISED_15S.md'
        t=p.read_text(encoding='utf-8')
        self.assertIn('拔刀指向对面的巨大鳄鱼',t)
        self.assertIn('4+3+5+3=15秒',t)
    def test_no_unapproved_attack(self):
        p=Path(__file__).resolve().parent/'fixtures/short_scene_v259/REVISED_15S.md'
        t=p.read_text(encoding='utf-8')
        self.assertIn('不张嘴、不扑击',t)
    def test_proposal_label(self):
        p=Path(__file__).resolve().parent/'fixtures/short_scene_v259/REVISED_15S.md'
        self.assertIn('导演提案',p.read_text(encoding='utf-8'))
if __name__=='__main__': unittest.main()
