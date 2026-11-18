import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from story_workflow import preflight, review, SPINE_FIELDS


def contract(ids=(1,), mode='single', endpoint='skill_independence'):
    return {'mode': mode, 'audience_promise': '学习者通过不替代操作得到一个真实技能回报。',
            'main_engine': '想掩饰失误与不得不现场验证的需求互相冲突。',
            'protagonist_strategy': '记录卡住的位置，只修改一个步骤，再让对方独立完成。',
            'ending_payoff': '顾客不用帮助就能完成组装，双方确认边界。',
            'endpoint_kind': endpoint, 'target_seconds': [90, 150],
            'episodes': [dict(number=n, scene_budgets=[{'scene': i, 'speech_seconds': 28,
                'independent_action_seconds': 10, 'pause_seconds': 5, 'overlapped_action_seconds': 4}
                for i in (1, 2, 3)], **{k: f'具体行动与代价：{k}，第{n}集' for k in SPINE_FIELDS}) for n in ids]}


def episode(number=1, day=9, extra=''):
    return f'''# EP{number:02d}｜试做
### SC01｜INT. 店内｜返乡第{day}日
△甲把未装好的零件摆在柜台上，乙压住了他要插入的手。
甲：今天先让顾客自己做，我只记住他卡在哪里。
乙：明天带上你的记录过来，我们在这里再试一次。
### SC02｜INT. 门厅｜同日
△顾客停下动作，甲没有伸手，转而挪动提示纸。
甲：你按刚才的顺序再试，错误也先留在纸上。
乙：这次我看得见提示，也能腾出手把东西放好。
### SC03｜EXT. 门口｜同日下午
△顾客独自把零件接好，乙将约定的六百元转给甲。
甲：这笔到账才能算收入，之前说好的还不能提前加。
乙：留好原来没做成的版本，下一次也可以照着查。
{extra}
'''


class StoryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, n=1, day=9, extra=''):
        p = self.root / f'EP{n:02d}.md'
        p.write_text(episode(n, day, extra), encoding='utf-8')
        return p

    def row(self, p, n=1, day=9):
        return {'number': n, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                'day': day, 'day_quote': f'返乡第{day}日'}

    def test_single_scope_and_generic_plan_are_rejected(self):
        c = contract((1, 2))
        self.assertIn('SINGLE_MODE_SCOPE_EXCEEDED', preflight(c)['issues'])
        c = contract(); c['episodes'][0]['payoff'] = '冲突升级'
        self.assertFalse(preflight(c)['contract_fields_present'])
        self.assertTrue(preflight(contract())['contract_fields_present'])

    def test_short_text_is_soft_not_permission_or_artistic_approval(self):
        p = self.write()
        result = review([p])
        self.assertTrue(result['text_complete_candidate'])
        self.assertTrue(result['mechanically_clear'])
        self.assertIn('SHORT_TEXT_REVIEW', [x['code'] for x in result['editorial_review_cues']])
        self.assertIsNone(result['artistic_approval'])
        self.assertIsNone(result['measured_runtime_seconds'])
        self.assertEqual(result['semantic_annotations_state'], 'unassessed')

    def test_explicit_duration_requires_pre_scene_budget_and_valid_arithmetic(self):
        c = contract(); del c['episodes'][0]['scene_budgets']
        self.assertIn('EP1_SCENE_BUDGETS_MISSING', preflight(c)['issues'])
        c = contract(); c['episodes'][0]['scene_budgets'][0]['speech_seconds'] = -1
        self.assertFalse(preflight(c)['contract_fields_present'])
        c = contract(); c['episodes'][0]['scene_budgets'][0]['overlapped_action_seconds'] = 100
        self.assertFalse(preflight(c)['contract_fields_present'])
        c = contract(); c['episodes'][0]['scene_budgets'][0]['pause_seconds'] = 100
        self.assertIn('EP1_SCENE_BUDGET_TOTAL_OUTSIDE_TARGET', preflight(c)['issues'])

    def test_postdraft_scene_count_and_speech_rate_are_checked(self):
        p = self.write(); c = contract()
        c['episodes'][0]['scene_budgets'] = [{'scene':1, 'speech_seconds':100,
            'independent_action_seconds':10, 'pause_seconds':5,'overlapped_action_seconds':0}]
        self.assertIn('SCENE_BUDGET_COUNT_MISMATCH', [x['code'] for x in review([p], c)['evidence_continuity_blockers']])
        c = contract(); c['episodes'][0]['scene_budgets'][0].update(speech_seconds=1, independent_action_seconds=37, overlapped_action_seconds=0)
        self.assertIn('SCENE_SPEECH_BUDGET_TOO_FAST', [x['code'] for x in review([p], c)['evidence_continuity_blockers']])

    def test_placeholder_missing_file_and_duplicate_remain_blockers(self):
        p = self.write(extra='△此处展开剩余争执，待补。')
        self.assertIn('UNWRITTEN_PLACEHOLDER', [x['code'] for x in review([p])['text_blockers']])
        self.assertFalse(review([self.root/'absent.md'])['mechanically_clear'])
        self.assertIn('DUPLICATE_EPISODE', [x['code'] for x in review([p, p])['text_blockers']])

    def test_contract_coverage_catches_unwritten_episode(self):
        result = review([self.write()], contract((1, 2), 'season'))
        self.assertIn('CONTRACT_SCOPE_MISMATCH', [x['code'] for x in result['text_blockers']])

    def test_next_day_conflict_uses_actual_quotes_and_bound_days(self):
        p, q = self.write(6, 9), self.write(7, 12)
        ledger = {'episodes': [self.row(p, 6, 9), self.row(q, 7, 12)], 'time_links': [{
            'source_episode': 6, 'target_episode': 7, 'offset_days': 1,
            'quote': '明天带上你的记录过来，我们在这里再试一次。'}]}
        result = review([p, q], ledger=ledger)
        conflicts = [x for x in result['evidence_continuity_blockers'] if x['code'] == 'RELATIVE_DAY_CONFLICT']
        self.assertEqual(conflicts[0]['detail']['expected_day'], 10)
        self.assertFalse(result['mechanically_clear'])
        q.write_text(episode(7, 10))
        ledger['episodes'][1] = self.row(q, 7, 10)
        self.assertTrue(review([p, q], ledger=ledger)['mechanically_clear'])

    def test_forged_day_hash_quote_and_duplicate_ledger_are_rejected(self):
        p = self.write(); row = self.row(p)
        row['day'] = 8
        self.assertFalse(review([p], ledger={'episodes': [row]})['mechanically_clear'])
        row = self.row(p); row['sha256'] = '0'*64
        self.assertFalse(review([p], ledger={'episodes': [row]})['mechanically_clear'])
        row = self.row(p); row['outcome_kind'] = 'content_service'; row['outcome_quote'] = '原稿根本不存在的成交动作'
        self.assertFalse(review([p], ledger={'episodes': [row]})['mechanically_clear'])
        self.assertFalse(review([p], ledger={'episodes': [self.row(p), self.row(p)]})['mechanically_clear'])

    def test_semantic_repetition_and_endpoint_mismatch_are_review_cues(self):
        files, rows = [], []
        for n in (1, 2, 3):
            p = self.write(n, n+8); files.append(p); row = self.row(p, n, n+8)
            row['mechanism'] = {'obstacle': '用户无法完成', 'tactic': '试做后改提示',
                'outcome': '客户验收', 'quote': '顾客停下动作，甲没有伸手，转而挪动提示纸。'}
            row['outcome_kind'] = 'content_service'
            row['outcome_quote'] = '顾客独自把零件接好，乙将约定的六百元转给甲。'
            rows.append(row)
        result = review(files, contract((1, 2, 3), 'season', 'audience_business'), {'episodes': rows})
        codes = [x['code'] for x in result['editorial_review_cues']]
        self.assertIn('REPEATED_DRAMATIC_MECHANISM_REVIEW', codes)
        self.assertIn('PROMISE_DELIVERY_MISMATCH_REVIEW', codes)
        self.assertTrue(result['mechanically_clear'])
        self.assertFalse(result['semantic_truth_verified'])

    def test_runtime_minimum_overrun_is_separate_from_text_completeness(self):
        p = self.write(extra='甲：'+'必须解释一个不同问题。'*100)
        result = review([p])
        self.assertTrue(result['text_complete_candidate'])
        self.assertTrue(result['duration_planning_blockers'])
        self.assertFalse(result['mechanically_clear'])

    def test_partial_review_not_silently_claimed_missing_scope(self):
        result = review([self.write(5), self.write(12)])
        self.assertTrue(result['text_complete_candidate'])
        self.assertIn('NONCONSECUTIVE_REVIEW_SCOPE', [x['code'] for x in result['editorial_review_cues']])

    def test_missing_ledger_rows_and_wrong_future_link_are_blockers(self):
        p, q = self.write(1, 1), self.write(2, 2)
        result = review([p, q], ledger={'episodes': [self.row(p, 1, 1)]})
        self.assertIn('MISSING_LEDGER_ROW', [x['code'] for x in result['evidence_continuity_blockers']])
        ledger = {'episodes': [self.row(p, 1, 1), self.row(q, 2, 2)], 'time_links': [{
            'source_episode': 1, 'target_episode': 2, 'offset_days': 2,
            'quote': '明天带上你的记录过来，我们在这里再试一次。'}]}
        self.assertIn('TIME_LINK_OFFSET_UNSUPPORTED', [x['code'] for x in review([p, q], ledger=ledger)['evidence_continuity_blockers']])

    def test_cli_bad_json_returns_failed_record_without_traceback(self):
        path = self.root/'bad.json'; path.write_text('{')
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('story_workflow.py')),
                              'preflight', str(path)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn('input_error', json.loads(run.stdout))

    def test_fresh_single_fixture_preserves_budget_and_evidence_bound_review(self):
        root = Path(__file__).resolve().parents[1] / 'tests/fixtures/v4_forward_shoe'
        c = json.loads((root/'story_contract.json').read_text())
        ledger = json.loads((root/'editorial_ledger.json').read_text())
        self.assertTrue(preflight(c)['contract_fields_present'])
        result = review([root/'EP01.md'], c, ledger)
        self.assertTrue(result['mechanically_clear'])
        self.assertIn('SHORT_TEXT_REVIEW', [x['code'] for x in result['editorial_review_cues']])
        self.assertIsNone(result['artistic_approval'])
        self.assertIsNone(result['measured_runtime_seconds'])

    def test_earlier_trial_budget_failure_is_not_retroactively_erased(self):
        root = Path(__file__).resolve().parents[1] / 'tests/fixtures/v4_forward_chair'
        c = json.loads((root/'story_contract.json').read_text())
        result = preflight(c)
        self.assertFalse(result['contract_fields_present'])
        self.assertIn('EP1_SCENE_BUDGETS_MISSING', result['issues'])
        self.assertIn('EP2_SCENE_BUDGETS_MISSING', result['issues'])


    def test_real_bare_heading_failure_is_recognized_without_source_rewrite(self):
        root = Path(__file__).resolve().parents[1] / 'tests/fixtures/v412_parcel_episode'
        p = root / 'EP01.raw.md'
        original = p.read_bytes()
        historical = json.loads((root / 'review.raw.json').read_text())
        self.assertIn('NO_SCENES', [x['code'] for x in historical['text_blockers']])
        result = review([p], json.loads((root / 'story_contract.json').read_text()))
        self.assertEqual(result['episodes'][0]['scenes'], 1)
        self.assertNotIn('NO_SCENES', [x['code'] for x in result['text_blockers']])
        self.assertEqual(result['episodes'][0]['sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(p.read_bytes(), original)
        self.assertEqual(result['semantic_annotations_state'], 'unassessed')
        self.assertIsNone(result['artistic_approval'])

    def test_plain_and_markdown_scene_headings_have_equivalent_diagnostics(self):
        p = self.write()
        baseline = review([p], contract())
        bare = re.sub(r'^### (?=SC)', '', p.read_text(), flags=re.M)
        p.write_text(bare)
        result = review([p], contract())
        for key in ('scenes', 'dialogue_han', 'dialogue_turns', 'body_han', 'runtime_proxy'):
            self.assertEqual(baseline['episodes'][0][key], result['episodes'][0][key])
        for key in ('text_blockers', 'evidence_continuity_blockers', 'editorial_review_cues'):
            self.assertEqual(baseline[key], result[key])
        for marker in ('INT.', 'EXT.', '内景', '外景'):
            with self.subTest(marker=marker):
                variant = re.sub(r'^(SC\d+)｜(?:INT\.|EXT\.)', rf'\1 {marker}', bare, flags=re.M)
                p.write_text(variant)
                self.assertEqual(review([p])['episodes'][0]['scenes'], 3)

    def test_bare_heading_scene_quotes_and_hash_binding_still_apply(self):
        p = self.write()
        original_row = self.row(p)
        p.write_text(re.sub(r'^### (?=SC)', '', p.read_text(), flags=re.M))
        quotes = ('甲把未装好的零件摆在柜台上', '顾客停下动作，甲没有伸手', '顾客独自把零件接好')
        ledger = {'episodes': [self.row(p)], 'scene_dispositions': [
            {'episode': 1, 'scene': i, 'decision': 'retain', 'quote': quote,
             'assessment': '本测试核对同场原文引句与场次绑定，不声称戏剧质量通过。'}
            for i, quote in enumerate(quotes, 1)]}
        result = review([p], contract(), ledger)
        self.assertEqual(result['evidence_continuity_blockers'], [])
        self.assertTrue(result['scene_review']['coverage_complete'])
        ledger['episodes'] = [original_row]
        stale = review([p], contract(), ledger)
        self.assertIn('LEDGER_HASH_MISMATCH', [x['code'] for x in stale['evidence_continuity_blockers']])

    def test_scene_mentions_and_sc_named_dialogue_do_not_create_scenes(self):
        for line in ('SC01：现在别进来。', 'SC01文件暂存',
                     '甲：SC01 INT. 屋内是我的文件名。', '△甲翻到SC01 INT.记录页。'):
            with self.subTest(line=line):
                p = self.root / 'mentions.md'
                p.write_text('# EP01《备注》\n' + line + '\n△甲关上门。\n甲：别进来。\n')
                result = review([p])
                self.assertEqual(result['episodes'][0]['scenes'], 0)
                self.assertIn('NO_SCENES', [x['code'] for x in result['text_blockers']])

    def test_legacy_helpers_keep_strict_defaults_after_modern_review(self):
        from audit_script_batch import audit as legacy_audit
        from audit_adversarial import inspect as legacy_inspect
        from audit_scene_depth import audit as legacy_depth
        from runtime_proxy import estimate as legacy_estimate
        p = self.write()
        p.write_text(re.sub(r'^### (?=SC)', '', p.read_text(), flags=re.M))
        self.assertEqual(review([p])['episodes'][0]['scenes'], 3)
        self.assertEqual(legacy_audit(p)['episodes'][0]['scenes'], 0)
        self.assertEqual(legacy_inspect(p)['episodes'][0]['scenes'], 0)
        self.assertEqual(legacy_depth(p)['episodes'][0]['scenes'], [])
        self.assertEqual(legacy_estimate(p)['episodes'][0]['scenes'], 0)

    def test_chinese_shot_script_headings_review_without_source_rewrite(self):
        from audit_script_batch import audit as legacy_audit
        p = self.root / 'shot_episode.md'
        source = '''# 短剧《测试》・第07集《旧摊》剧本正文

## 分镜剧本

### 场景一・夜市（外・夜）

**【镜 1】 全景** ｜ 00:00–00:05
摊主把手机架在饵盒上，画面里只有他的脸，桌面上的账本落在镜头外。
摊主（低声）：先拍清楚这一次。

### 闪回一・旧屋（内・夜）

**【镜 2】 近景**
母亲收回伸向少年的手，转而把哥哥拉到身边。
▎画外（母亲，回荡）：先让你哥去。
'''
        p.write_text(source, encoding='utf-8')
        original = p.read_bytes()
        result = review([p])
        codes = [x['code'] for x in result['text_blockers']]
        self.assertEqual(result['episodes'][0]['episode'], 7)
        self.assertEqual(result['episodes'][0]['scenes'], 2)
        self.assertEqual(result['episodes'][0]['dialogue_turns'], 2)
        self.assertNotIn('NO_EPISODE_HEADINGS', codes)
        self.assertNotIn('NO_SCENES', codes)
        self.assertNotIn('NO_EXPLICIT_STAGE_ACTION', codes)
        self.assertEqual(result['episodes'][0]['sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(p.read_bytes(), original)
        self.assertEqual(legacy_audit(p)['episodes'], [])

    def test_explicit_playable_section_excludes_notes_from_metrics_and_evidence(self):
        p = self.root / 'shot_episode_with_notes.md'
        source = '''# 短剧《测试》・第07集《旧摊》剧本正文

## 本集人物
摊主：本集人物说明里的台词不算进场次。
> 本集任务：这里写作者希望观众看到什么。

## 分镜剧本

### 场景一・夜市（外・夜）
**【镜 1】 全景** ｜ 00:00–00:05
摊主把手机架在饵盒上，转身将被风吹翻的账页压在水杯下面。
摊主：这次把鱼漂拍清楚。

### 场景二・河边（外・日）
**【镜 2】 近景**
父亲蹲下来，伸手把线结从石缝里慢慢解开。
父亲：你先自己看漂，别急着收竿。

## 结尾钩子说明
作者说明：父亲还要留一句预告给下一集，这不是已发生的情节。

## 拍摄提示
甲：本提示里的对白也不应计入剧本台词。
'''
        p.write_text(source, encoding='utf-8')
        original = p.read_bytes()
        result = review([p])
        row = result['episodes'][0]
        self.assertEqual(row['scenes'], 2)
        self.assertEqual(row['dialogue_turns'], 2)
        self.assertEqual(row['dialogue_han'], 19)
        self.assertEqual(result['source_sections'][0]['mode'], 'explicit_playable_section')
        self.assertEqual(row['sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(p.read_bytes(), original)
        ledger = {'episodes': [{'number': 7, 'sha256': row['sha256'],
            'outcome_kind': 'earned_boundary',
            'outcome_quote': '作者说明：父亲还要留一句预告给下一集'}]}
        checked = review([p], ledger=ledger)
        self.assertIn('OUTCOME_EVIDENCE_INVALID', [x['code'] for x in checked['evidence_continuity_blockers']])

    def test_authored_shot_timecodes_supersede_dialogue_only_duration_proxy(self):
        p = self.root / 'timed_episode.md'
        p.write_text('''# EP01｜已排时长
### SC01｜INT. 屋内
**【镜 1】** ｜ 00:00–00:30
△甲把写着旧日期的账本翻到最后一页，逐项核对桌上的收据。
甲：先把日期对上。
**【镜 2】** ｜ 00:30–01:00
△乙将两张收据并排放好，指出其中一张的店名被换掉。
乙：这张不是我们店的。
**【镜 3】** ｜ 01:00–01:35
△甲收起被换过的收据，把原账本推到镜头前。
甲：那就把原账公开。
''', encoding='utf-8')
        result = review([p])
        row = result['episodes'][0]
        self.assertEqual(row['authored_timing']['planned_span_seconds'], 95)
        self.assertTrue(row['authored_timing']['sufficient_for_planned_span_review'])
        self.assertEqual(row['runtime_assessment_basis'], 'author_supplied_shot_timecodes_unmeasured')
        self.assertIsNone(row['authored_timing']['measured_runtime_seconds'])
        codes = [cue['code'] for cue in result['editorial_review_cues']]
        self.assertNotIn('RUNTIME_PROXY_BELOW_TARGET_REVIEW', codes)



if __name__ == '__main__':
    unittest.main()
