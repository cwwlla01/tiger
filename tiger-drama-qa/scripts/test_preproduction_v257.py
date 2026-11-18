import unittest,json,tempfile
from pathlib import Path
from audit_preproduction_v257 import audit
P=Path(__file__).resolve().parent.parent/'fixtures/v257-preproduction/production_plan.json'
class TestPreproduction(unittest.TestCase):
 def test_baseline(self):self.assertEqual(audit(P)['status'],'TEXT_PLAN_COMPLETE_WITH_LAYOUT_BLOCK')
 def mutate(self,shot,key,value):
  p=json.loads(P.read_text(encoding='utf-8'));next(s for s in p['shots'] if s['id']==shot)[key]=value
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'plan.json';f.write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8');self.assertEqual(audit(f)['status'],'INVALID')
 def test_wrong_text(self):self.mutate('S01B','exact_text','第三声前别回头')
 def test_voice_reveal(self):self.mutate('S04','reveal_outside',True)
 def test_voice_order(self):self.mutate('S04','order','VOICE_BEFORE_KNOCK')
 def test_hand_reveal(self):self.mutate('S06','reveal_identity',True)
 def test_door_open(self):self.mutate('S06','door_open',True)
 def test_false_unblock(self):self.mutate('S07','status','READY')
 def test_false_video(self):
  p=json.loads(P.read_text(encoding='utf-8'));p['video_status']='VIDEO_PASSED'
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'plan.json';f.write_text(json.dumps(p,ensure_ascii=False),encoding='utf-8');self.assertEqual(audit(f)['status'],'INVALID')
 def test_wrong_edit(self):self.mutate('S09','route','TEXT_TO_VIDEO')
if __name__=='__main__':unittest.main()
