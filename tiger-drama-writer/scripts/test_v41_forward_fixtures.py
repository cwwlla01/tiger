import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from story_workflow import preflight,review


class V41ForwardFixtures(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]/'tests/fixtures'

    def load(self,name,file):
        return json.loads((self.root/name/file).read_text())

    def test_scope_selection_and_scene_counts_do_not_inherit_three_scene_template(self):
        c = self.load('v41_forward_fishing','story_contract.json')
        self.assertEqual(c['workflow_revision'],'4.1')
        self.assertEqual(c['scope_basis']['count_source'],'inferred')
        self.assertEqual(len(c['episodes']),1)
        self.assertEqual(len(c['episodes'][0]['scene_budgets']),2)
        self.assertTrue(preflight(c)['contract_fields_present'])
        c = self.load('v41_forward_cafe','story_contract.json')
        self.assertEqual(c['scope_basis']['count_source'],'user_fixed')
        self.assertEqual(len(c['episodes'][0]['scene_budgets']),1)
        self.assertTrue(preflight(c)['contract_fields_present'])

    def test_actual_revised_samples_bind_review_without_claiming_timing_or_art(self):
        for name,file,ledger_file in [('v41_forward_fishing','EP01.md','editorial_ledger.json'),
                                      ('v41_forward_cafe','EP01_revised.md','editorial_ledger_revised.json')]:
            with self.subTest(name=name):
                c = self.load(name,'story_contract.json')
                ledger = self.load(name,ledger_file)
                d = review([self.root/name/file],c,ledger)
                self.assertTrue(d['mechanically_clear'])
                self.assertEqual(d['editorial_readiness'],'source_bound_self_review_only')
                self.assertIsNone(d['artistic_approval'])
                self.assertIsNone(d['measured_runtime_seconds'])
                self.assertFalse(d['independent_reader_review'])

    def test_short_cafe_raw_proxy_and_real_revision_are_preserved(self):
        name = 'v41_forward_cafe';root = self.root/name
        c = self.load(name,'story_contract.json');ledger = self.load(name,'editorial_ledger_raw.json')
        d = review([root/'EP01_raw.md'],c,ledger)
        self.assertLess(d['episodes'][0]['runtime_proxy']['estimated_seconds_range'][1],90)
        self.assertIn('RUNTIME_PROXY_BELOW_TARGET_REVIEW',[x['code'] for x in d['editorial_review_cues']])
        self.assertNotEqual((root/'EP01_raw.md').read_bytes(),(root/'EP01_revised.md').read_bytes())
        self.assertIsNone(d['measured_runtime_seconds'])


if __name__ == '__main__':
    unittest.main()
