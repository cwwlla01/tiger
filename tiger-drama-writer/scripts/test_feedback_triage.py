import hashlib
import json
import unittest
from feedback_triage import triage_emotion, triage_voice
from audit_emotion_panel import fingerprint

class FeedbackTriageTest(unittest.TestCase):
    def test_empty_emotion_never_invents(self):
        script=b'scene'; ledger={'script_sha256':hashlib.sha256(script).hexdigest()}
        r=triage_emotion(script,ledger,{'status':'not_collected','readers':[]})
        self.assertEqual(r['status'],'awaiting_external_feedback')
        self.assertIsNone(r['reader_metrics'])
        self.assertFalse(r['revision_candidates'])

    def test_valid_emotion_prioritizes_real_scores(self):
        script=b'ep'; ledger={'script_sha256':hashlib.sha256(script).hexdigest()}
        panel={'status':'completed','script_sha256':ledger['script_sha256'],'ledger_sha256':fingerprint(ledger),'readers':[]}
        for i in range(3):
            panel['readers'].append({'reader_id':f'reader{i}', 'collected_by':'tester', 'evidence_ref':f'file_{i}',
                'ratings':{'choice_credibility':4, 'consequence_clarity':4, 'relationship_change':3, 'emotional_impact':2+i},
                'most_effective_moment':'具体有效的动作细节', 'least_convincing_moment':'角色突然改变了立场', 'reason':'没有给出足够的行动证据'})
        r=triage_emotion(script,ledger,panel)
        self.assertEqual(r['status'],'editorial_triage_required')
        self.assertEqual(r['revision_candidates'][0]['dimension'],'emotional_impact')
        self.assertFalse(r['human_revision_approved'])
        self.assertTrue(r['revision_candidates'][0]['reader_disagreement'])

    def test_empty_voice_never_invents(self):
        blind={'cards':[{'id':'c1'}],'candidate_roles':['A','B']}; key={'c1':{'role':'A'}}
        r=triage_voice(blind,key,{'status':'not_collected','readers':[]})
        self.assertIsNone(r['reader_metrics'])
        self.assertEqual(r['status'],'awaiting_external_feedback')

    def test_voice_confusion_is_observed(self):
        blind={'cards':[{'id':'c1'},{'id':'c2'}],'candidate_roles':['A','B']}; key={'c1':{'role':'A'},'c2':{'role':'B'}}
        h=hashlib.sha256(json.dumps(blind,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        panel={'blind_sha256':h,'status':'completed','readers':[{'reader_id':f'reader{i}','collected_by':'tester','evidence_ref':f'proof{i}', 'answers':{'c1':'B','c2':'B'}} for i in range(3)]}
        r=triage_voice(blind,key,panel)
        self.assertEqual(r['revision_candidates'][0]['true_role'],'A')
        self.assertEqual(r['revision_candidates'][0]['confusions'],3)
        self.assertFalse(r['human_revision_approved'])

if __name__=='__main__': unittest.main()
