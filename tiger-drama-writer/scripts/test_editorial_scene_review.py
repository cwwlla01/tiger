import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from story_workflow import preflight, review
from test_story_workflow import contract, episode


class EditorialSceneReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root/'EP01.md'
        self.path.write_text(episode())
        self.ledger = {'episodes': [{'number': 1,
            'sha256': hashlib.sha256(self.path.read_bytes()).hexdigest()}]}
        self.quotes = [
            '甲把未装好的零件摆在柜台上，乙压住了他要插入的手。',
            '顾客停下动作，甲没有伸手，转而挪动提示纸。',
            '顾客独自把零件接好，乙将约定的六百元转给甲。']

    def tearDown(self):
        self.temp.cleanup()

    def decisions(self, decision='retain'):
        return [{'episode': 1, 'scene': n, 'decision': decision, 'quote': q,
                 'assessment': '本场短但有试做受阻、改变提示位置及实物交付，停顿承担反应，不补同义对白。'}
                for n,q in enumerate(self.quotes, 1)]

    def test_v41_records_count_source_without_rewriting_legacy_contracts(self):
        old = contract()
        self.assertTrue(preflight(old)['contract_fields_present'])
        new = dict(old, workflow_revision='4.1')
        self.assertIn('SCOPE_BASIS_MISSING', preflight(new)['issues'])
        new['scope_basis'] = {'count_source': 'inferred',
            'episode_count_reason': '一次争执与当场归还可闭合，不推迟到下集。',
            'merge_review': '取件与第一次受阻合一场，改策与实际归还合第二场。'}
        self.assertTrue(preflight(new)['contract_fields_present'])
        new['scope_basis']['count_source'] = 'guessed_user_fact'
        self.assertIn('INVALID_COUNT_SOURCE', preflight(new)['issues'])
        self.assertNotIn('workflow_revision', old)
        self.assertFalse(preflight(dict(old, workflow_revision='4.11'))['contract_fields_present'])

    def test_mechanical_clear_does_not_hide_unreviewed_scenes(self):
        result = review([self.path], ledger=self.ledger)
        self.assertTrue(result['mechanically_clear'])
        self.assertEqual(result['editorial_readiness'], 'awaiting_scene_review')
        self.assertEqual(len(result['scene_review']['unreviewed_scenes']), 3)
        self.assertIsNone(result['artistic_approval'])

    def test_user_fixed_multiepisode_count_is_not_silently_shortened(self):
        c = contract((1,2),'season')
        c['workflow_revision'] = '4.1'
        c['scope_basis'] = {'count_source':'user_fixed',
            'episode_count_reason':'用户给定集数，用两次不同的选择兑现结尾。',
            'merge_review':'每集改变下一集的资源与人物关系，不合并为同一次争执。'}
        self.assertIn('FIXED_EPISODE_COUNT_MISSING',preflight(c)['issues'])
        c['scope_basis']['requested_episode_count'] = 3
        self.assertIn('FIXED_EPISODE_COUNT_MISMATCH',preflight(c)['issues'])
        c['scope_basis']['requested_episode_count'] = 2
        self.assertTrue(preflight(c)['contract_fields_present'])

    def test_partial_review_cannot_clear_remaining_scenes(self):
        self.ledger['scene_dispositions'] = self.decisions()[:1]
        result = review([self.path], ledger=self.ledger)
        self.assertEqual(result['editorial_readiness'], 'awaiting_scene_review')
        self.assertEqual(result['scene_review']['unreviewed_scenes'],
                         [{'episode': 1, 'scene': 2}, {'episode': 1, 'scene': 3}])

    def test_complete_annotation_is_only_self_review_not_artistic_approval(self):
        self.ledger['scene_dispositions'] = self.decisions()
        result = review([self.path], ledger=self.ledger)
        self.assertTrue(result['scene_review']['coverage_complete'])
        self.assertEqual(result['editorial_readiness'], 'source_bound_self_review_only')
        self.assertFalse(result['scene_review']['artistic_meaning_verified'])
        self.assertFalse(result['independent_reader_review'])
        self.assertIsNone(result['measured_runtime_seconds'])

    def test_neighbor_scene_quote_is_not_evidence_for_this_scene(self):
        self.ledger['scene_dispositions'] = self.decisions()
        self.ledger['scene_dispositions'][0]['quote'] = self.quotes[1]
        result = review([self.path], ledger=self.ledger)
        self.assertIn('SCENE_DISPOSITION_QUOTE_INVALID',
                      [x['code'] for x in result['evidence_continuity_blockers']])
        self.assertFalse(result['mechanically_clear'])

    def test_rewrite_merge_and_unresolved_remain_pending(self):
        for decision in ('rewrite', 'merge', 'unresolved'):
            with self.subTest(decision=decision):
                self.ledger['scene_dispositions'] = self.decisions()
                self.ledger['scene_dispositions'][1]['decision'] = decision
                result = review([self.path], ledger=self.ledger)
                self.assertEqual(result['editorial_readiness'], 'revision_pending')
                self.assertTrue(result['scene_review']['coverage_complete'])
                self.assertEqual(result['scene_review']['pending_revision_scenes'], [{'episode': 1, 'scene': 2}])

    def test_stale_hash_cannot_clear_scene_review(self):
        self.ledger['scene_dispositions'] = self.decisions()
        self.ledger['episodes'][0]['sha256'] = '0'*64
        result = review([self.path], ledger=self.ledger)
        self.assertEqual(result['editorial_readiness'], 'blocked_by_mechanics')
        self.assertFalse(result['scene_review']['coverage_complete'])

    def test_duplicate_invalid_scene_and_empty_reason_are_rejected(self):
        cases = []
        a = self.decisions(); a.append(dict(a[0])); cases.append((a,'DUPLICATE_SCENE_DISPOSITION'))
        a = self.decisions(); a[0]['scene'] = 99; cases.append((a,'SCENE_DISPOSITION_SCENE_INVALID'))
        a = self.decisions(); a[0]['assessment'] = '没问题'; cases.append((a,'SCENE_DISPOSITION_REASON_INVALID'))
        a = self.decisions(); a[0]['assessment'] = 'PASS'; cases.append((a,'SCENE_DISPOSITION_REASON_INVALID'))
        for decisions,code in cases:
            with self.subTest(code=code):
                self.ledger['scene_dispositions'] = decisions
                result = review([self.path], ledger=self.ledger)
                self.assertIn(code,[x['code'] for x in result['evidence_continuity_blockers']])

    def test_final_cli_flag_rejects_pending_and_accepts_only_annotated_state(self):
        ledger_path = self.root/'ledger.json'
        script = str(Path(__file__).with_name('story_workflow.py'))
        def run():
            ledger_path.write_text(json.dumps(self.ledger,ensure_ascii=False))
            return subprocess.run([sys.executable,script,'review',str(self.path),'--ledger',
                                   str(ledger_path),'--require-scene-review'],capture_output=True,text=True)
        pending = run()
        self.assertEqual(pending.returncode,2)
        self.assertTrue(json.loads(pending.stdout)['mechanically_clear'])
        self.ledger['scene_dispositions'] = self.decisions()
        complete = run()
        self.assertEqual(complete.returncode,0)
        self.assertIsNone(json.loads(complete.stdout)['artistic_approval'])

    def test_real_thin_scene_regression_stays_pending_after_mechanical_pass(self):
        root = Path(__file__).resolve().parents[1]/'tests/fixtures/v41_thin_regression'
        ledger = json.loads((root/'editorial_ledger.json').read_text())
        result = review([root/'EP02.raw.md'], ledger=ledger)
        self.assertTrue(result['mechanically_clear'])
        self.assertTrue(result['scene_review']['coverage_complete'])
        self.assertEqual(result['editorial_readiness'], 'revision_pending')
        self.assertIn({'episode': 2, 'scene': 2}, result['scene_review']['pending_revision_scenes'])
        self.assertIsNone(result['artistic_approval'])


if __name__ == '__main__':
    unittest.main()
