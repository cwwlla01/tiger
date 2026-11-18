#!/usr/bin/env python3
"""Joint first-pass screen; static pass never hides a runtime-proxy overrun.

A proxy is not a rehearsal measurement. This script cannot grant editorial approval.
"""
import argparse
import json
from pathlib import Path
from episode_stop_gate import check
from runtime_proxy import estimate


def assess(file, episode, maximum_seconds=150):
    if maximum_seconds <= 0:
        raise ValueError('maximum_seconds must be positive')
    static = check(file, episode)
    rows = estimate(file)['episodes']
    issues = list(static['issues'])
    if len(rows) != 1 or rows[0]['episode'] != episode:
        issues.append('PROXY_WRONG_EPISODE')
        runtime = None
        status = 'UNAVAILABLE'
    else:
        runtime = rows[0]
        low, high = runtime['estimated_seconds_range']
        status = 'MINIMUM_EXCEEDS_TARGET' if low > maximum_seconds else ('UPPER_EXCEEDS_TARGET' if high > maximum_seconds else 'WITHIN_PROXY_TARGET')
        if status == 'MINIMUM_EXCEEDS_TARGET':
            issues.append('RUNTIME_PROXY_MINIMUM_EXCEEDS_TARGET')
        elif status == 'UPPER_EXCEEDS_TARGET':
            pass  # uncertainty: review via beat plan; do not force a destructive rewrite
    return {
        'episode': episode, 'source_sha256': static['sha256'],
        'static_pass': static['static_ready_for_editorial_review'],
        'static_issues': static['issues'], 'runtime_proxy': runtime,
        'runtime_proxy_status': status,
        'needs_rewrite_before_next_episode': bool(issues),
        'requires_beat_plan_or_rehearsal': status == 'UPPER_EXCEEDS_TARGET',
        'time_decision': ('REWRITE' if status == 'MINIMUM_EXCEEDS_TARGET' else ('REVIEW_NOT_PROVED' if status == 'UPPER_EXCEEDS_TARGET' else 'PROXY_FEASIBLE_NOT_PROVED')), 
        'issues': issues, 'editorial_approved': False,
        'real_rehearsal_measured': False, 'next_episode_authorized': False,
        'note': 'Even a clean proxy is not measured runtime; independent editorial and rehearsal gates remain required.'
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('file')
    p.add_argument('--episode', type=int, required=True)
    p.add_argument('--max-seconds', type=int, default=150)
    p.add_argument('--output')
    a = p.parse_args()
    result = assess(a.file, a.episode, a.max_seconds)
    content = json.dumps(result, ensure_ascii=False, indent=2)
    if a.output:
        Path(a.output).write_text(content, encoding='utf-8')
    print(content)
    raise SystemExit(2 if result['needs_rewrite_before_next_episode'] else 0)
