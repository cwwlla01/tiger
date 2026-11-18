import hashlib,json,tempfile,unittest
from pathlib import Path
from verify_timing_plan import verify
SCRIPT='## EP04｜试拍\n### SC01｜门口｜夜｜外\n△他把手递过去，然后走到门外。\n甲：现在就走。\n乙：我陪你走。\n'
class TimingTest(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name)/'ep.md';self.q=Path(self.t.name)/'plan.json'
  self.p.write_text(SCRIPT,encoding='utf8')
  self.plan={'episode':4,'sha256':hashlib.sha256(self.p.read_bytes()).hexdigest(),'scenes':[{'scene':1,'beats':[{'physical_action':'走到门口','action_quote':'他把手递过去，然后走到门外。','action_seconds':94,'speech_seconds':6,'overlap':False,'speech_lines':['甲：现在就走。','乙：我陪你走。']}]}]}
 def tearDown(self):self.t.cleanup()
 def check(self):
  self.q.write_text(json.dumps(self.plan,ensure_ascii=False),encoding='utf8');return verify(self.p,self.q)
 def test_pass(self):self.assertTrue(self.check()['plan_screening_pass'])
 def test_all_action_overlapped_risk(self):
  self.plan['scenes'][0]['beats'][0]['overlap']=True
  self.assertIn('ALL_ACTION_TIME_ASSUMED_OVERLAPPED',self.check()['issues'])
 def test_script_hash(self):
  self.p.write_text(SCRIPT+'△他停下。',encoding='utf8');self.assertIn('SCRIPT_HASH_MISMATCH',self.check()['issues'])
 def test_duration(self):
  self.plan['scenes'][0]['beats'][0]['action_seconds']=160;self.assertIn('PLAN_OUTSIDE_90_150',self.check()['issues'])
 def test_speed(self):
  self.plan['scenes'][0]['beats'][0].update(action_seconds=100,speech_seconds=.2);self.assertIn('SCENE1_BEAT1_DIALOGUE_TOO_FAST',self.check()['issues'])
 def test_missing_overlap(self):
  del self.plan['scenes'][0]['beats'][0]['overlap'];self.assertIn('SCENE1_BEAT1_OVERLAP_UNSPECIFIED',self.check()['issues'])
 def test_missing_dialogue(self):
  self.plan['scenes'][0]['beats'][0]['speech_lines']=[]
  self.assertIn('SCENE1_DIALOGUE_COVERAGE_MISMATCH',self.check()['issues'])
 def test_duplicate_dialogue(self):
  b=self.plan['scenes'][0]['beats'][0];b['speech_lines']+=b['speech_lines']
  self.assertIn('SCENE1_DIALOGUE_COVERAGE_MISMATCH',self.check()['issues'])
 def test_fake_action(self):
  self.plan['scenes'][0]['beats'][0]['action_quote']='他突然跳上直升飞机逃走并离开这个现场'
  self.assertIn('SCENE1_BEAT1_ACTION_NOT_IN_STAGE_DIRECTION',self.check()['issues'])
 def test_dialogue_cannot_be_action_quote(self):
  b=self.plan['scenes'][0]['beats'][0]
  b['action_quote']='甲：现在就走。乙：我陪你走。'
  self.assertIn('SCENE1_BEAT1_ACTION_NOT_IN_STAGE_DIRECTION',self.check()['issues'])
 def test_reused_action_evidence(self):
  b=self.plan['scenes'][0]['beats'][0]
  self.plan['scenes'][0]['beats']=[dict(b,speech_lines=b['speech_lines'][:1]),dict(b,speech_lines=b['speech_lines'][1:],speech_seconds=5)]
  self.assertIn('SCENE1_BEAT2_ACTION_EVIDENCE_REUSED',self.check()['issues'])
 def test_reversed_actions(self):
  self.p.write_text(SCRIPT.replace('△他把手递过去，然后走到门外。','△他先打开房门，听见门轴响了一声。\n△他把手递过去，然后走到门外。'),encoding='utf8')
  self.plan['sha256']=hashlib.sha256(self.p.read_bytes()).hexdigest()
  b=self.plan['scenes'][0]['beats'][0]
  first=dict(b,action_quote='他把手递过去，然后走到门外。',speech_lines=b['speech_lines'][:1])
  second=dict(b,action_quote='他先打开房门，听见门轴响了一声。',speech_lines=b['speech_lines'][1:],speech_seconds=5)
  self.plan['scenes'][0]['beats']=[first,second]
  self.assertIn('SCENE1_BEAT2_ACTION_ORDER_REVERSED',self.check()['issues'])
 def test_unattributed_speech(self):
  self.plan['scenes'][0]['beats'][0]['speech_lines']=[]
  self.assertIn('SCENE1_BEAT1_UNATTRIBUTED_SPEECH_TIME',self.check()['issues'])
if __name__=='__main__':unittest.main()
