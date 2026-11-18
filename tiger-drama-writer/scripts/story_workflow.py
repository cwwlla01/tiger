#!/usr/bin/env python3
"""V4 planning/diagnostics; evidence provenance is not artistic certification.

Keep legacy validators unchanged. Numeric length/line warnings are soft here.
Only entered, source-bound time links can be checked deterministically.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

from audit_script_batch import SC as LEGACY_SC, audit, han
from audit_adversarial import inspect
from audit_scene_depth import audit as scene_audit
from runtime_proxy import estimate

# Broader screenplay notation is opt-in in this V4 workflow; standalone legacy tools
# keep their strict defaults and all checks remain bound to the original source bytes.
EP = re.compile(
    r'^[ \t]*#{1,2}[ \t]*(?![^\n]*/[ \t]*SC[ \t]*\d+)'
    r'(?=[^\n]*?(?:\bEP[ \t]*0*|第[ \t]*0*)(\d{1,3})'
    r'(?:[ \t]*集|(?=[《\s｜|：:—–-]|$)))[^\n]*$',
    re.I | re.M,
)
SC = re.compile(
    rf'(?:{LEGACY_SC.pattern})|'
    r'(?:^[ \t]*SC[ \t]*\d+(?:[ \t]+|[｜|：:—–-][ \t]*)'
    r'(?:INT\.|EXT\.|内景|外景)(?=[ \t｜|：:—–-]|$)[^\n]*$)',
    re.I | re.M,
)
SC = re.compile(
    rf'(?:{SC.pattern})|'
    r'(?:^[ \t]*#{2,4}[ \t]*(?:场景?[一二三四五六七八九十百\d]+|闪回[一二三四五六七八九十百\d]+)'
    r'(?=[ \t｜|：:—–·・（(\-]|$)[^\n]*$)',
    re.I | re.M,
)
SPEECH = re.compile(
    r'^[ \t]*(?:▎(?=画外))?'
    r'(?:\*\*([^*\n]{1,24})\*\*|([\u3400-\u9fffA-Za-z][\u3400-\u9fffA-Za-z0-9·_-]{0,15}))'
    r'(?:\([^\n)]*\)|（[^\n）]*）)?[ \t]*[：:][ \t]*(.+)$',
    re.M,
)
SHOT = re.compile(
    r'^[ \t]*\*\*【镜(?:头)?[ \t]*\d+】[^\n]*\*\*'
    r'(?:[ \t]*[｜|][ \t]*\d{2}:\d{2}[ \t]*[–—-][ \t]*\d{2}:\d{2})?[ \t]*$',
    re.M,
)
SHOT_TIMECODE = re.compile(
    r'^[ \t]*\*\*【镜(?:头)?[ \t]*\d+】[^\n]*\*\*[ \t]*[｜|][ \t]*'
    r'(\d{2}):(\d{2})[ \t]*[–—-][ \t]*(\d{2}):(\d{2})[ \t]*$',
    re.M,
)
PLAYABLE_START = re.compile(r'^[ \t]*#{1,4}[ \t]*分镜剧本[ \t]*$', re.M)
EDITORIAL_TAIL = re.compile(
    r'^[ \t]*#{1,4}[ \t]*(?:结尾钩子说明|拍摄提示|本集人物|本集任务|衔接)(?:[ \t：:].*)?$',
    re.M,
)


def playable_body(body):
    """Use an explicitly marked playable section when present; preserve other source formats."""
    starts = list(PLAYABLE_START.finditer(body))
    if not starts:
        return body, 'unmarked_full_episode'
    if len(starts) != 1:
        return body, 'ambiguous_playable_sections'
    start = starts[0]
    tail = EDITORIAL_TAIL.search(body, start.end())
    end = tail.start() if tail else len(body)
    return body[start.end():end], 'explicit_playable_section'


def analysis_source(text):
    """Retain episode headings but remove clearly labeled author/production material."""
    headings = list(EP.finditer(text))
    if not headings:
        return text, []
    pieces, sections = [], []
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body, mode = playable_body(text[heading.end():end])
        pieces.extend((heading.group(0), '\n', body, '\n'))
        sections.append({'episode': int(heading.group(1)), 'mode': mode})
    return ''.join(pieces), sections


def authored_shot_timing(body, min_coverage=0.8):
    """Extract a planned shot-time span; never call it measured runtime."""
    shots = list(SHOT.finditer(body))
    matches = list(SHOT_TIMECODE.finditer(body))
    ranges = []
    invalid = 0
    for match in matches:
        start = int(match.group(1)) * 60 + int(match.group(2))
        end = int(match.group(3)) * 60 + int(match.group(4))
        if end <= start:
            invalid += 1
        else:
            ranges.append((start, end))
    ordered = all(ranges[i][0] >= ranges[i-1][0] for i in range(1, len(ranges)))
    sufficient = bool(shots and len(ranges) >= 3 and len(matches) / len(shots) >= min_coverage
                      and invalid == 0 and ordered)
    return {
        'basis': 'author_supplied_shot_timecodes',
        'planned_span_seconds': max((end for _, end in ranges), default=0)
                               - min((start for start, _ in ranges), default=0) if ranges else None,
        'timed_shots': len(matches), 'total_shots': len(shots),
        'coverage_ratio': round(len(matches) / len(shots), 3) if shots else 0.0,
        'invalid_ranges': invalid, 'time_ordered': ordered,
        'sufficient_for_planned_span_review': sufficient,
        'measured_runtime_seconds': None,
    }


def has_explicit_stage_action(body):
    if re.search(r'^\s*(?:△|ACTION\s*:)', body, re.M | re.I):
        return True
    shots = list(SHOT.finditer(body))
    for i, shot in enumerate(shots):
        chunk = body[shot.end():shots[i+1].start() if i+1 < len(shots) else len(body)]
        narration = SPEECH.sub('', chunk)
        narration = re.sub(r'^\s*▎字幕[^\n]*$', '', narration, flags=re.M)
        if han(narration) >= 8:
            return True
    return False

PLAN_FIELDS = ('audience_promise', 'main_engine', 'protagonist_strategy',
               'ending_payoff', 'endpoint_kind')
SPINE_FIELDS = ('attempt', 'counteraction', 'choice', 'payoff', 'cost',
                'mainline_change', 'mechanism', 'next_trigger')
GENERIC = {'冲突升级', '剧情推进', '获得成长', '下集更精彩', 'conflict escalates', 'tbd', 'todo'}
DAY = re.compile(r'第\s*(\d+)\s*[日天]')
SCENE_CUES = {'SCENE_UNDERDEVELOPED_REVIEW', 'SCENE_DIALOGUE_TOO_SPARSE_REVIEW'}


def concrete(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in GENERIC


def preflight(data):
    issues = []
    if not isinstance(data, dict):
        return {'contract_fields_present': False, 'issues': ['CONTRACT_NOT_OBJECT'],
                'creative_quality_certified': False}
    if data.get('mode') not in {'single', 'season', 'retrospective', 'review'}:
        issues.append('INVALID_MODE')
    if 'workflow_revision' in data and data['workflow_revision'] not in {'4.0', '4.1'}:
        issues.append('UNSUPPORTED_WORKFLOW_REVISION')
    if data.get('workflow_revision') == '4.1':
        scope = data.get('scope_basis')
        if not isinstance(scope, dict):
            issues.append('SCOPE_BASIS_MISSING')
        else:
            if scope.get('count_source') not in {'user_fixed', 'inferred', 'inherited_assumption'}:
                issues.append('INVALID_COUNT_SOURCE')
            for key in ('episode_count_reason', 'merge_review'):
                if not concrete(scope.get(key)):
                    issues.append('SCOPE_' + key.upper() + '_MISSING')
    for key in PLAN_FIELDS:
        if not concrete(data.get(key)):
            issues.append('MISSING_OR_GENERIC_' + key.upper())
    target = data.get('target_seconds', [90, 150])
    if (not isinstance(target, list) or len(target) != 2
            or any(type(n) not in (int, float) or not math.isfinite(n) or n <= 0 for n in target)
            or target[0] > target[1]):
        issues.append('INVALID_TARGET_SECONDS')
    if 'silent' in data and type(data['silent']) is not bool:
        issues.append('INVALID_SILENT_FLAG')
    episodes = data.get('episodes')
    ids = []
    if not isinstance(episodes, list) or not episodes:
        issues.append('MISSING_EPISODE_SPINE')
    else:
        for row in episodes:
            if not isinstance(row, dict):
                issues.append('INVALID_SPINE_ROW')
                continue
            number = row.get('number')
            if type(number) is not int or number < 1:
                issues.append('INVALID_EPISODE_ID')
            else:
                ids.append(number)
            for key in SPINE_FIELDS:
                if not concrete(row.get(key)):
                    issues.append(f'EP{number}_{key.upper()}_MISSING_OR_GENERIC')
            if 'target_seconds' in data:
                budgets = row.get('scene_budgets')
                if not isinstance(budgets, list) or not budgets:
                    issues.append(f'EP{number}_SCENE_BUDGETS_MISSING')
                else:
                    total = 0
                    valid_budgets = True
                    for scene_n, budget in enumerate(budgets, 1):
                        if not isinstance(budget, dict) or budget.get('scene') != scene_n:
                            valid_budgets = False
                            continue
                        keys = ('speech_seconds', 'independent_action_seconds', 'pause_seconds', 'overlapped_action_seconds')
                        if any(type(budget.get(k)) not in (int, float)
                               or not math.isfinite(budget[k]) or budget[k] < 0 for k in keys):
                            valid_budgets = False
                            continue
                        if budget['overlapped_action_seconds'] > budget['speech_seconds']:
                            valid_budgets = False
                        total += sum(budget[k] for k in keys[:3])
                    if not valid_budgets:
                        issues.append(f'EP{number}_SCENE_BUDGETS_INVALID')
                    elif 'INVALID_TARGET_SECONDS' not in issues and not target[0] <= total <= target[1]:
                        issues.append(f'EP{number}_SCENE_BUDGET_TOTAL_OUTSIDE_TARGET')
        if len(ids) == len(episodes) and ids != list(range(ids[0], ids[0] + len(ids))):
            issues.append('SPINE_IDS_NOT_CONSECUTIVE_INCREASING')
        if data.get('mode') == 'single' and len(episodes) != 1:
            issues.append('SINGLE_MODE_SCOPE_EXCEEDED')
    if (data.get('workflow_revision') == '4.1' and isinstance(data.get('scope_basis'), dict)
            and data['scope_basis'].get('count_source') == 'user_fixed'):
        requested = data['scope_basis'].get('requested_episode_count')
        if requested is None and data.get('mode') == 'single':
            requested = 1
        if type(requested) is not int or requested < 1:
            issues.append('FIXED_EPISODE_COUNT_MISSING')
        elif not isinstance(episodes, list) or len(episodes) != requested:
            issues.append('FIXED_EPISODE_COUNT_MISMATCH')
    debts = data.get('payoff_debts', [])
    if not isinstance(debts, list):
        issues.append('INVALID_PAYOFF_DEBTS')
    else:
        seen = set()
        for debt in debts:
            if not isinstance(debt, dict):
                issues.append('INVALID_PAYOFF_DEBT')
                continue
            ident, setup, due = debt.get('id'), debt.get('setup_episode'), debt.get('due_episode')
            if not isinstance(ident, str) or not ident.strip() or ident in seen:
                issues.append('INVALID_OR_DUPLICATE_DEBT_ID')
            else:
                seen.add(ident)
            if type(setup) is not int or type(due) is not int or setup not in ids or due < setup:
                issues.append('INVALID_DEBT_EPISODES')
            if not concrete(debt.get('promised_result')):
                issues.append('MISSING_DEBT_RESULT')
    return {'contract_fields_present': not issues, 'issues': sorted(set(issues)),
            'episode_ids': ids, 'creative_quality_certified': False,
            'caveat': 'Populated planning fields do not prove a good story or actual future payoff.'}


def finding(code, episode=None, detail=None):
    row = {'code': code}
    if episode is not None:
        row['episode'] = episode
    if detail is not None:
        row['detail'] = detail
    return row


def quote_ok(text, quote, minimum=8):
    return isinstance(quote, str) and len(quote.strip()) >= minimum and text.count(quote) == 1


def scene_dispositions(cues, sources, valid_ledger, ledger):
    """Verify scene-review coverage, never whether the editorial reason is true."""
    required = {(c['episode'], c['detail']['scene']) for c in cues
                if c['code'] in SCENE_CUES and isinstance(c.get('detail'), dict)}
    errors, decisions, addressed, pending, seen = [], [], set(), set(), set()
    records = ledger.get('scene_dispositions', []) if isinstance(ledger, dict) else []
    if not isinstance(records, list):
        errors.append(finding('INVALID_SCENE_DISPOSITIONS'))
        records = []
    for record in records:
        if not isinstance(record, dict):
            errors.append(finding('INVALID_SCENE_DISPOSITION'))
            continue
        n, scene = record.get('episode'), record.get('scene')
        if type(n) is not int or type(scene) is not int or n not in valid_ledger or scene < 1:
            errors.append(finding('SCENE_DISPOSITION_SOURCE_INVALID'))
            continue
        key = (n, scene)
        if key in seen:
            errors.append(finding('DUPLICATE_SCENE_DISPOSITION', n, {'scene': scene}))
            continue
        seen.add(key)
        body = sources[n]['text']
        cuts = list(SC.finditer(body))
        if scene > len(cuts):
            errors.append(finding('SCENE_DISPOSITION_SCENE_INVALID', n, {'scene': scene}))
            continue
        chunk = body[cuts[scene-1].end():cuts[scene].start() if scene < len(cuts) else None]
        if not quote_ok(chunk, record.get('quote')):
            errors.append(finding('SCENE_DISPOSITION_QUOTE_INVALID', n, {'scene': scene}))
            continue
        decision, assessment = record.get('decision'), record.get('assessment')
        if (decision not in {'retain', 'rewrite', 'merge', 'unresolved'}
                or not concrete(assessment)
                or assessment.strip().casefold() in {'保留', '通过', '没问题', '无问题', 'pass', 'okay', 'ok', 'retain', 'approved'}):
            errors.append(finding('SCENE_DISPOSITION_REASON_INVALID', n, {'scene': scene}))
            continue
        addressed.add(key)
        if decision != 'retain':
            pending.add(key)
        decisions.append({'episode': n, 'scene': scene, 'decision': decision,
                          'quote': record['quote'], 'assessment': assessment})
    def keys(items):
        return [{'episode': n, 'scene': s} for n, s in sorted(items)]
    return {'required_scenes': keys(required), 'unreviewed_scenes': keys(required-addressed),
            'pending_revision_scenes': keys(pending), 'decisions': decisions,
            'coverage_complete': not errors and not (required-addressed),
            'artistic_meaning_verified': False}, errors


def review(files, contract=None, ledger=None):
    hard, evidence_errors, duration_blocks, soft, rows = [], [], [], [], []
    sources = {}
    section_rows = []
    min_seconds, max_seconds = 90, 150
    if contract is not None:
        checked = preflight(contract)
        if not checked['contract_fields_present']:
            evidence_errors.append(finding('CONTRACT_INVALID', detail=checked['issues']))
        else:
            min_seconds, max_seconds = contract.get('target_seconds', [90, 150])
    for filename in files:
        try:
            path = Path(filename)
            raw = path.read_bytes()
            text = raw.decode('utf-8')
        except (OSError, UnicodeError) as error:
            hard.append(finding('UNREADABLE_SOURCE', detail={'file': str(filename), 'error': str(error)}))
            continue
        diagnostic_text, sections = analysis_source(text)
        parsed = audit(path, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH,
                       source_text=diagnostic_text)
        if parsed.get('error'):
            hard.append(finding('NO_EPISODE_HEADINGS', detail=str(path)))
            continue
        adversarial = inspect(path, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH,
                              source_text=diagnostic_text)['episodes']
        depths = scene_audit(path, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH,
                             source_text=diagnostic_text)['episodes']
        timings = estimate(path, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH,
                           source_text=diagnostic_text)['episodes']
        headings = list(EP.finditer(diagnostic_text))
        raw_headings = list(EP.finditer(text))
        section_rows.extend({'file': str(path), **item} for item in sections)
        for idx, ep in enumerate(parsed['episodes']):
            n = ep['episode']
            raw_body = text[raw_headings[idx].end():raw_headings[idx+1].start()
                            if idx+1 < len(raw_headings) else len(text)]
            body, section_mode = playable_body(raw_body)
            if n in sources:
                hard.append(finding('DUPLICATE_EPISODE', n))
            else:
                sources[n] = {'text': body, 'sha256': hashlib.sha256(raw).hexdigest(),
                              'file': str(path), 'one_episode_per_file': len(headings) == 1,
                              'source_section': section_mode}
            if ep['scenes'] == 0:
                hard.append(finding('NO_SCENES', n))
            if not has_explicit_stage_action(body):
                hard.append(finding('NO_EXPLICIT_STAGE_ACTION', n))
            if ep['dialogue_turns'] == 0 and not (isinstance(contract, dict) and contract.get('silent') is True):
                hard.append(finding('NO_SPOKEN_DIALOGUE', n))
            flags = adversarial[idx]['adversarial_flags']
            if 'PLACEHOLDER' in ep['heuristic_flags'] or 'UNWRITTEN_PLACEHOLDER_BLOCKER' in flags:
                hard.append(finding('UNWRITTEN_PLACEHOLDER', n))
            for flag in ep['heuristic_flags']:
                if flag != 'PLACEHOLDER':
                    soft.append(finding(flag, n))
            for flag in flags:
                if flag != 'UNWRITTEN_PLACEHOLDER_BLOCKER':
                    soft.append(finding(flag, n))
            for scene_index, scene in enumerate(depths[idx]['scenes'], 1):
                for flag in scene['flags']:
                    soft.append(finding(flag, n, {'scene': scene_index}))
            timing = timings[idx]
            shot_timing = authored_shot_timing(body)
            if ep['dialogue_han'] == 0:
                soft.append(finding('PROXY_UNAVAILABLE_NON_CHINESE_OR_SILENT', n))
                timing = {'estimated_seconds_range': None, 'measured_runtime_seconds': None}
                runtime_basis = 'unavailable'
            elif shot_timing['sufficient_for_planned_span_review']:
                runtime_basis = 'author_supplied_shot_timecodes_unmeasured'
                planned = shot_timing['planned_span_seconds']
                if planned < min_seconds or planned > max_seconds:
                    soft.append(finding('AUTHORED_TIMECODE_SPAN_OUTSIDE_TARGET_REVIEW', n, shot_timing))
            else:
                runtime_basis = 'dialogue_and_scene_proxy_unmeasured'
                low, high = timing['estimated_seconds_range']
                if low > max_seconds:
                    duration_blocks.append(finding('RUNTIME_PROXY_MINIMUM_EXCEEDS_TARGET', n, timing))
                elif high > max_seconds:
                    soft.append(finding('RUNTIME_PROXY_UPPER_EXCEEDS_TARGET', n, timing))
                elif high < min_seconds:
                    soft.append(finding('RUNTIME_PROXY_BELOW_TARGET_REVIEW', n, timing))
            rows.append({'episode': n, 'file': str(path), 'sha256': hashlib.sha256(raw).hexdigest(),
                         'scenes': ep['scenes'], 'dialogue_han': ep['dialogue_han'],
                         'dialogue_turns': ep['dialogue_turns'], 'body_han': ep['body_han'],
                         'runtime_proxy': timing, 'authored_timing': shot_timing,
                         'runtime_assessment_basis': runtime_basis})
    ids = sorted(sources)
    if ids and ids != list(range(ids[0], ids[-1] + 1)):
        soft.append(finding('NONCONSECUTIVE_REVIEW_SCOPE'))
    if not files or not rows:
        hard.append(finding('NO_SCREENPLAY_EPISODES'))
    if isinstance(contract, dict) and preflight(contract)['contract_fields_present']:
        expected = [e['number'] for e in contract['episodes']]
        if ids != expected:
            hard.append(finding('CONTRACT_SCOPE_MISMATCH', detail={'expected': expected, 'actual': ids}))
        if 'target_seconds' in contract:
            for planned in contract['episodes']:
                n = planned['number']
                if n not in sources:
                    continue
                cuts = list(SC.finditer(sources[n]['text']))
                budgets = planned['scene_budgets']
                if len(cuts) != len(budgets):
                    evidence_errors.append(finding('SCENE_BUDGET_COUNT_MISMATCH', n))
                    continue
                for scene_i, cut in enumerate(cuts):
                    chunk = sources[n]['text'][cut.end():cuts[scene_i+1].start() if scene_i+1 < len(cuts) else None]
                    spoken_han = sum(han(content) for _, _, content in SPEECH.findall(chunk))
                    if spoken_han / 5 > budgets[scene_i]['speech_seconds'] + 0.001:
                        evidence_errors.append(finding('SCENE_SPEECH_BUDGET_TOO_FAST', n,
                                                       {'scene': scene_i+1, 'dialogue_han': spoken_han}))

    valid_ledger = {}
    if ledger is None:
        soft.append(finding('SEMANTIC_LEDGER_NOT_SUPPLIED'))
    elif not isinstance(ledger, dict) or not isinstance(ledger.get('episodes'), list):
        evidence_errors.append(finding('INVALID_EDITORIAL_LEDGER'))
    else:
        signatures = defaultdict(list)
        seen = set()
        for item in ledger['episodes']:
            if not isinstance(item, dict) or type(item.get('number')) is not int:
                evidence_errors.append(finding('INVALID_LEDGER_ROW'))
                continue
            n = item['number']
            if n in seen:
                evidence_errors.append(finding('DUPLICATE_LEDGER_ROW', n))
                continue
            seen.add(n)
            if n not in sources:
                evidence_errors.append(finding('UNEXPECTED_LEDGER_EPISODE', n))
                continue
            src = sources[n]
            before = len(evidence_errors)
            if not src['one_episode_per_file']:
                evidence_errors.append(finding('LEDGER_REQUIRES_EPISODE_FILES', n))
            if item.get('sha256') != src['sha256']:
                evidence_errors.append(finding('LEDGER_HASH_MISMATCH', n))
            if 'day' in item or 'day_quote' in item:
                day, quote = item.get('day'), item.get('day_quote')
                if (type(day) is not int or day < 0 or not quote_ok(src['text'], quote, 3)
                        or {int(m) for m in DAY.findall(quote or '')} != {day}):
                    evidence_errors.append(finding('DAY_ANCHOR_INVALID', n))
            mechanism = item.get('mechanism')
            if mechanism is not None:
                if (not isinstance(mechanism, dict)
                        or any(not concrete(mechanism.get(k)) for k in ('obstacle', 'tactic', 'outcome'))
                        or not quote_ok(src['text'], mechanism.get('quote'))):
                    evidence_errors.append(finding('MECHANISM_EVIDENCE_INVALID', n))
            if 'outcome_kind' in item or 'outcome_quote' in item:
                if not concrete(item.get('outcome_kind')) or not quote_ok(src['text'], item.get('outcome_quote')):
                    evidence_errors.append(finding('OUTCOME_EVIDENCE_INVALID', n))
            if len(evidence_errors) == before:
                valid_ledger[n] = item
                if mechanism is not None:
                    key = tuple(mechanism[k].strip().casefold() for k in ('obstacle', 'tactic', 'outcome'))
                    signatures[key].append(n)
        for n in set(sources) - seen:
            evidence_errors.append(finding('MISSING_LEDGER_ROW', n))
        for signature, episode_ids in signatures.items():
            if len(episode_ids) >= 3:
                soft.append(finding('REPEATED_DRAMATIC_MECHANISM_REVIEW', detail={
                    'episodes': episode_ids, 'obstacle_tactic_outcome': list(signature)}))
        links = ledger.get('time_links', [])
        if not isinstance(links, list):
            evidence_errors.append(finding('INVALID_TIME_LINKS'))
            links = []
        for link in links:
            if not isinstance(link, dict):
                evidence_errors.append(finding('INVALID_TIME_LINK'))
                continue
            src_n, dst_n, offset = link.get('source_episode'), link.get('target_episode'), link.get('offset_days')
            if (type(src_n) is not int or type(dst_n) is not int or type(offset) is not int
                    or src_n not in valid_ledger or dst_n not in valid_ledger or src_n >= dst_n):
                evidence_errors.append(finding('TIME_LINK_EPISODES_INVALID'))
                continue
            quote = link.get('quote')
            if not quote_ok(sources[src_n]['text'], quote):
                evidence_errors.append(finding('TIME_LINK_QUOTE_INVALID', src_n))
                continue
            cues = set()
            if '明天' in quote or '次日' in quote:
                cues.add(1)
            if '后天' in quote:
                cues.add(2)
            if cues != {offset}:
                evidence_errors.append(finding('TIME_LINK_OFFSET_UNSUPPORTED', src_n))
                continue
            source_day, target_day = valid_ledger[src_n].get('day'), valid_ledger[dst_n].get('day')
            if source_day is None or target_day is None:
                evidence_errors.append(finding('TIME_LINK_DAY_MISSING', src_n))
            elif source_day + offset != target_day:
                evidence_errors.append(finding('RELATIVE_DAY_CONFLICT', src_n, {
                    'target_episode': dst_n, 'expected_day': source_day + offset,
                    'actual_day': target_day, 'quote': quote}))
        if ids and isinstance(contract, dict) and concrete(contract.get('endpoint_kind')):
            actual = valid_ledger.get(ids[-1], {}).get('outcome_kind')
            if actual is None:
                soft.append(finding('FINAL_OUTCOME_NOT_ASSESSED', ids[-1]))
            elif actual != contract['endpoint_kind']:
                soft.append(finding('PROMISE_DELIVERY_MISMATCH_REVIEW', ids[-1], {
                    'promised_kind': contract['endpoint_kind'], 'delivered_kind': actual,
                    'quote': valid_ledger[ids[-1]]['outcome_quote']}))
    scene_review, scene_errors = scene_dispositions(soft, sources, valid_ledger, ledger)
    evidence_errors.extend(scene_errors)
    mechanically_clear = bool(rows) and not (hard or evidence_errors or duration_blocks)
    if not mechanically_clear:
        editorial_state = 'blocked_by_mechanics'
    elif scene_review['pending_revision_scenes']:
        editorial_state = 'revision_pending'
    elif scene_review['unreviewed_scenes']:
        editorial_state = 'awaiting_scene_review'
    elif not valid_ledger:
        editorial_state = 'unassessed'
    else:
        editorial_state = 'source_bound_self_review_only'
    return {'policy_version': '4.1', 'mode': contract.get('mode') if isinstance(contract, dict) else 'review',
            'episodes': rows, 'text_blockers': hard, 'evidence_continuity_blockers': evidence_errors,
            'duration_planning_blockers': duration_blocks, 'editorial_review_cues': soft,
            'source_sections': section_rows,
            'text_complete_candidate': bool(rows) and not hard,
            'mechanically_clear': mechanically_clear,
            'scene_review': scene_review, 'editorial_readiness': editorial_state,
            'semantic_annotations_state': 'source_bound_annotations_only' if valid_ledger else 'unassessed',
            'semantic_truth_verified': False, 'artistic_approval': None,
            'independent_reader_review': False, 'measured_runtime_seconds': None,
            'caveat': 'Soft cues are not rewrite orders; hashes and labels do not prove narrative meaning. No rehearsal, audience or artistic certification.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    plan = subs.add_parser('preflight')
    plan.add_argument('contract')
    plan.add_argument('--output')
    rev = subs.add_parser('review')
    rev.add_argument('files', nargs='+')
    rev.add_argument('--contract')
    rev.add_argument('--ledger')
    rev.add_argument('--require-scene-review', action='store_true',
                     help='Fail on pending/unassessed scene review, without certifying artistic quality.')
    rev.add_argument('--output')
    args = parser.parse_args(argv)
    try:
        contract = json.loads(Path(args.contract).read_text()) if args.contract else None
        if args.command == 'preflight':
            result = preflight(contract)
            success = result['contract_fields_present']
        else:
            ledger = json.loads(Path(args.ledger).read_text()) if args.ledger else None
            result = review(args.files, contract, ledger)
            success = result['mechanically_clear']
            if args.require_scene_review:
                success = success and result['editorial_readiness'] == 'source_bound_self_review_only'
    except (OSError, ValueError, TypeError) as error:
        result = {'input_error': str(error), 'mechanically_clear': False,
                  'artistic_approval': None, 'measured_runtime_seconds': None}
        success = False
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + '\n', encoding='utf-8')
    print(payload)
    return 0 if success else 2


if __name__ == '__main__':
    raise SystemExit(main())
