#!/usr/bin/env python3
"""Evidence-presence gate for editorial genre-contract claims, not semantic quality judgment."""
import argparse
import json
import re
from pathlib import Path

REQUIRED = ('ability_setup', 'ability_use', 'obstacle_changed', 'cost_or_limit', 'end_state')


def check(script_path, manifest_path):
    content = Path(script_path).read_text(encoding='utf-8')
    data = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    issues = []
    if data.get('genre') != 'power_progression':
        issues.append('UNSUPPORTED_GENRE_FOR_THIS_GATE')
    entries = data.get('episodes')
    if not isinstance(entries, list) or not entries:
        return {'evidence_ready': False, 'issues': ['NO_EPISODES'], 'episodes': []}
    # Evidence must appear inside the claimed episode, never somewhere else in the batch.
    episode_parts = {}
    starts = list(re.finditer(r'(?m)^#{1,3}\s*EP\s*0*(\d+)\b', content, re.I))
    for i, match in enumerate(starts):
        number = int(match.group(1))
        if number in episode_parts:
            issues.append(f'DUPLICATE_EPISODE_HEADER_EP{number:02d}')
        episode_parts[number] = content[match.start():starts[i+1].start() if i+1 < len(starts) else len(content)]
    results = []
    for e in entries:
        ep = e.get('episode')
        eid = f'EP{ep:02d}' if isinstance(ep, int) else str(ep)
        row_issues = []
        scope = episode_parts.get(ep) if isinstance(ep, int) else None
        if scope is None:
            row_issues.append('EPISODE_HEADER_NOT_FOUND')
            scope = ''
        deferred = e.get('payoff_deferred') is True
        if deferred and (not isinstance(e.get('payoff_debt_due'), int) or not isinstance(e.get('defer_reason'), str) or len(e['defer_reason']) < 8):
            row_issues.append('DEFERRAL_WITHOUT_DEBT')
        for key in (('cost_or_limit', 'end_state') if deferred else REQUIRED):
            quote = e.get(key)
            if not isinstance(quote, str) or len(quote.strip()) < 6:
                row_issues.append(f'{key.upper()}_MISSING')
            elif quote not in scope:
                row_issues.append(f'{key.upper()}_NOT_IN_CLAIMED_EPISODE')
        if not isinstance(e.get('power_gain'), dict):
            row_issues.append('POWER_GAIN_LEDGER_MISSING')
        else:
            pg = e['power_gain']
            if pg.get('new_points', 0) and (not pg.get('verified_source') or 'balance_after' not in pg):
                row_issues.append('UNVERIFIED_POWER_GAIN')
        results.append({'episode': eid, 'issues': row_issues, 'evidence_present': not row_issues})
    if not any(not e.get('payoff_deferred') for e in entries):
        issues.append('NO_DELIVERED_PAYOFF_IN_WINDOW')
    return {'evidence_ready': not issues and all(x['evidence_present'] for x in results), 'issues': issues, 'episodes': results,
            'human_review_required': ['quote_context_and_true_causality', 'genre_satisfaction', 'continuity_and_cost', 'performed_runtime'],
            'note': 'Literal evidence presence is not semantic proof. A quote can be present yet fail to demonstrate a real payoff.'}


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('manifest')
    ap.add_argument('--output')
    args=ap.parse_args()
    result=check(args.script,args.manifest)
    output=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output: Path(args.output).write_text(output,encoding='utf-8')
    print(output)
    raise SystemExit(0 if result['evidence_ready'] else 1)
