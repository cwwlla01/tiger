import copy,unittest
from audit_dialogue_power_v215 import audit
B={'beat_id':'B1','source_anchor':'S1','speaker_id':'A','listener_ids':['B'],'line_or_silence':'别动','eyeline_target':'B','screen_axis':'east-west','knowledge_after':'B hears warning'}
C=dict(B,beat_id='B2',speaker_id='B',listener_ids=['A'],line_or_silence='silence',eyeline_target='door',knowledge_after='B suspects danger')
def fixture():
    d={'beats':[copy.deepcopy(B),copy.deepcopy(C)]}
    return {'stages':{s:{'takes':[{'take_id':'T1','dialogue_power':copy.deepcopy(d)}]} for s in ('03','04','05')}}
class TestDialoguePower(unittest.TestCase):
    def test_clean(self): self.assertEqual(audit(fixture()),[])
    def test_speaker(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'][0]['speaker_id']='B';self.assertTrue(any('SPEAKER_ID_DRIFT' in e for e in audit(x)))
    def test_listener(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'][0]['listener_ids']=[];self.assertTrue(any('LISTENER_IDS_DRIFT' in e for e in audit(x)))
    def test_dialogue(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'][0]['line_or_silence']='走';self.assertTrue(any('LINE_OR_SILENCE_DRIFT' in e for e in audit(x)))
    def test_axis(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'][0]['screen_axis']='north-south';self.assertTrue(any('SCREEN_AXIS_DRIFT' in e for e in audit(x)))
    def test_eyeline(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'][0]['eyeline_target']='A';self.assertTrue(any('EYELINE_TARGET_DRIFT' in e for e in audit(x)))
    def test_knowledge(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'][0]['knowledge_after']='unknown';self.assertTrue(any('KNOWLEDGE_AFTER_DRIFT' in e for e in audit(x)))
    def test_order(self):
        x=fixture();x['stages']['05']['takes'][0]['dialogue_power']['beats'].reverse();self.assertTrue(any('BEAT_ORDER_DRIFT' in e for e in audit(x)))
    def test_missing(self):
        x=fixture();del x['stages']['04']['takes'][0]['dialogue_power'];self.assertTrue(any('MISSING_DIALOGUE_POWER' in e for e in audit(x)))
    def test_invented(self):
        x=fixture();x['stages']['04']['takes'][0]['dialogue_power']['beats'].append(dict(B,beat_id='B3'));self.assertTrue(any('INVENTED_FRAME_BEAT' in e for e in audit(x)))
    def test_missing_source(self):
        x=fixture();x['stages']['03']['takes'][0]['dialogue_power']['beats'][0]['source_anchor']='';self.assertTrue(any('MISSING_source_anchor' in e for e in audit(x)))
    def test_self_listener(self):
        x=fixture();x['stages']['03']['takes'][0]['dialogue_power']['beats'][0]['listener_ids']=['A'];self.assertTrue(any('SELF_LISTENER' in e for e in audit(x)))
if __name__=='__main__':unittest.main()
