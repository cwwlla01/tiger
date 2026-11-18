import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from firstpass_dual_gate import assess

BASE = '''## EP01｜样稿
'''
SCENE = '''\n### SC{n}｜楼道｜晨｜内
△有人抱着纸箱奔跑，门突然卡住，另一人拿起钥匙尝试开锁，但门没有动。她停下呼吸，寻找别的出口。\n甲：{speech}\n乙：你要先说清楚，现在谁负责把东西搬到楼下？\n甲：我负责，但需要你把钥匙交出来，否则我们都要迟到。\n乙：可以，不过你必须答应不再拿别人的工作开玩笑。\n甲：我答应。我们先试一次，如果失败就走侧门。\n△两人换了位置，他把箱子抬高，她试着推门。一次不成又试第二次，终于发现门闩上有一截塑料袋。\n'''

def make(phrase):
    return BASE + ''.join(SCENE.format(n=i,speech=phrase) for i in range(1,4))

class DualGateTests(unittest.TestCase):
    def runtext(self, content):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'EP01.md';p.write_text(content,encoding='utf-8');return assess(p,1)
    def test_long_dialogue_is_not_approved(self):
        result=self.runtext(make('你先别动这个箱子。'*75))
        self.assertIn('RUNTIME_PROXY_MINIMUM_EXCEEDS_TARGET',result['issues'])
        self.assertFalse(result['next_episode_authorized'])
    def test_static_failure_is_not_approved(self):
        result=self.runtext('## EP01｜空稿\n### SC01｜一间房\n甲：你好')
        self.assertFalse(result['static_pass'])
        self.assertTrue(result['needs_rewrite_before_next_episode'])
    def test_wrong_episode_is_not_approved(self):
        result=self.runtext(make('我知道。'))
        self.assertFalse(result['next_episode_authorized'])
        self.assertFalse(result['editorial_approved'])
    def test_uncertain_upper_is_review_not_forced_rewrite(self):
        # A normal three-scene draft may have conservative upper > 150;
        # this requires a beat plan, not compulsory deletion of dramatic substance.
        result=self.runtext(make('现在先把箱子稳住，我们再想别的办法。'))
        self.assertEqual(result['runtime_proxy_status'],'UPPER_EXCEEDS_TARGET')
        self.assertTrue(result['requires_beat_plan_or_rehearsal'])
        self.assertNotIn('RUNTIME_PROXY_UPPER_EXCEEDS_TARGET_REVIEW', result['issues'])
        self.assertFalse(result['next_episode_authorized'])
    def test_invalid_limit(self):
        with self.assertRaises(ValueError):
            assess(__file__,1,0)
if __name__=='__main__':unittest.main()
