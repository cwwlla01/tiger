import copy
import hashlib
import unittest
from audit_emotion_panel import audit, fingerprint


class EmotionPanelTest(unittest.TestCase):
    def setUp(self):
        self.script = '## EP01\n### SC01\n周宁：别走。'.encode()
        self.ledger = {'script_sha256': hashlib.sha256(self.script).hexdigest()}
        self.panel = {'status': 'completed', 'script_sha256': self.ledger['script_sha256'],
                      'ledger_sha256': fingerprint(self.ledger), 'readers': []}
        for i in range(3):
            self.panel['readers'].append({'reader_id': f'reader{i}', 'collected_by': 'external editor',
                'evidence_ref': f'recording-{i}', 'ratings': {'choice_credibility': 3,
                'consequence_clarity': 4, 'relationship_change': 4, 'emotional_impact': 2},
                'most_effective_moment': '她选择留下来承担后果',
                'least_convincing_moment': '结尾情绪停顿仍然太短', 'reason': '人物选择可信但情绪发挥还不足'})

    def test_good(self):
        x = audit(self.script, self.ledger, self.panel)
        self.assertTrue(x['mechanically_valid'])
        self.assertEqual(x['rating_means']['emotional_impact'], 2)
        self.assertFalse(x['independent_people_verified'])
        self.assertFalse(x['artistic_quality_certified'])

    def test_missing_panel(self):
        p = copy.deepcopy(self.panel); p['status'] = 'not_collected'; p['readers'] = []
        x = audit(self.script, self.ledger, p)
        self.assertFalse(x['mechanically_valid']); self.assertIsNone(x['rating_means'])

    def test_mutated_script(self):
        self.assertFalse(audit(self.script + b'!', self.ledger, self.panel)['mechanically_valid'])

    def test_mutated_ledger(self):
        l = dict(self.ledger); l['character'] = 'Z'
        self.assertFalse(audit(self.script, l, self.panel)['mechanically_valid'])

    def test_duplicate_reader(self):
        p = copy.deepcopy(self.panel); p['readers'][1]['reader_id'] = 'reader0'
        self.assertFalse(audit(self.script, self.ledger, p)['mechanically_valid'])

    def test_duplicate_evidence(self):
        p = copy.deepcopy(self.panel); p['readers'][1]['evidence_ref'] = 'recording-0'
        self.assertFalse(audit(self.script, self.ledger, p)['mechanically_valid'])

    def test_invalid_rating(self):
        p = copy.deepcopy(self.panel); p['readers'][1]['ratings']['emotional_impact'] = True
        self.assertFalse(audit(self.script, self.ledger, p)['mechanically_valid'])

    def test_missing_response(self):
        p = copy.deepcopy(self.panel); p['readers'][2]['reason'] = ''
        self.assertFalse(audit(self.script, self.ledger, p)['mechanically_valid'])

    def test_insufficient_readers(self):
        p = copy.deepcopy(self.panel); p['readers'] = p['readers'][:2]
        self.assertFalse(audit(self.script, self.ledger, p)['mechanically_valid'])


if __name__ == '__main__': unittest.main()
