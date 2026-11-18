import hashlib
import json
import unittest
from audit_voice_panel import audit

BLIND = {'source_sha256': 'source', 'candidate_roles': ['甲', '乙'], 'cards': [{'id':'C001','line':'那就马上走吧'}, {'id':'C002','line':'可我还有问题'}]}
KEY = {'C001': {'role':'甲'}, 'C002': {'role':'乙'}}
HASH = hashlib.sha256(json.dumps(BLIND, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def panel(n=3):
    return {'status':'completed', 'blind_sha256':HASH, 'readers':[{'reader_id':f'r{i:03d}', 'collected_by':'external person', 'evidence_ref':f'ref-{i}', 'answers':{'C001':'甲','C002':'乙'}} for i in range(n)]}
class PanelTests(unittest.TestCase):
    def test_valid(self):
        a = audit(BLIND, KEY, panel()); self.assertTrue(a['mechanically_valid']); self.assertEqual(a['accuracy'],1.0); self.assertFalse(a['independent_people_verified'])
    def test_no_actual_panel(self):
        p=panel(0); p['status']='not_collected'; self.assertFalse(audit(BLIND,KEY,p)['mechanically_valid'])
    def test_insufficient(self): self.assertFalse(audit(BLIND,KEY,panel(2))['mechanically_valid'])
    def test_duplicates(self):
        p=panel(); p['readers'][1]['reader_id']=p['readers'][0]['reader_id']; self.assertFalse(audit(BLIND,KEY,p)['mechanically_valid'])
    def test_missing_answer(self):
        p=panel(); p['readers'][0]['answers'].pop('C002'); self.assertFalse(audit(BLIND,KEY,p)['mechanically_valid'])
    def test_bad_hash(self):
        p=panel(); p['blind_sha256']='old'; self.assertFalse(audit(BLIND,KEY,p)['mechanically_valid'])
    def test_bad_role(self):
        p=panel(); p['readers'][0]['answers']['C002']='丙'; self.assertFalse(audit(BLIND,KEY,p)['mechanically_valid'])
    def test_missing_evidence(self):
        p=panel(); p['readers'][0]['evidence_ref']=''; self.assertFalse(audit(BLIND,KEY,p)['mechanically_valid'])
    def test_key_mismatch(self):
        key=dict(KEY); key.pop('C002'); self.assertFalse(audit(BLIND,key,panel())['mechanically_valid'])
if __name__ == '__main__': unittest.main()
