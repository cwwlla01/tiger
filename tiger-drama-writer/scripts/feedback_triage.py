#!/usr/bin/env python3
"""Build provenance-preserving revision candidates from external panel results.

Never fabricate reader scores and never automatically authorise a revision.
"""
import argparse
import hashlib
import json
from pathlib import Path

from audit_emotion_panel import audit as audit_emotion, DIMENSIONS
from audit_voice_panel import audit as audit_voice


def sha(data):
    return hashlib.sha256(data).hexdigest()


def triage_emotion(script, ledger, panel):
    report = audit_emotion(script, ledger, panel)
    base = {'mode': 'emotion', 'script_sha256': sha(script), 'panel_record_sha256': sha(json.dumps(panel, sort_keys=True, ensure_ascii=False).encode()),
            'human_revision_approved': False, 'verified_readers': False, 'issues': report['issues']}
    if not report['mechanically_valid']:
        return {**base, 'status': 'awaiting_external_feedback', 'revision_candidates': [], 'reader_metrics': None}
    readers = panel['readers']
    means = report['rating_means']
    # Rank by observed dimensions, not a made-up pass threshold.
    priorities = sorted(DIMENSIONS, key=lambda d: (means[d], d))
    flags = []
    for dim in priorities:
        values = [r['ratings'][dim] for r in readers]
        flags.append({'dimension': dim, 'mean': means[dim], 'range': [min(values), max(values)],
                      'reader_disagreement': max(values)-min(values) >= 2,
                      'editorial_action': 'Find the exact scene and propose a concrete action/counteraction revision; require editor approval before editing.'})
    feedback = [{'reader_id': r['reader_id'], 'least_convincing_moment': r['least_convincing_moment'], 'reason': r['reason'],
                 'most_effective_moment': r['most_effective_moment']} for r in readers]
    return {**base, 'status': 'editorial_triage_required', 'reader_metrics': means,
            'revision_candidates': flags, 'qualitative_feedback': feedback,
            'next_step': 'Human editor selects a scene and records its exact quotation; preserve original draft, create a distinct revised file, invalidate old panel for revised hash.'}


def triage_voice(blind, key, panel):
    report = audit_voice(blind, key, panel)
    base = {'mode': 'voice', 'blind_pack_sha256': sha(json.dumps(blind, sort_keys=True, ensure_ascii=False).encode()),
            'human_revision_approved': False, 'verified_readers': False, 'issues': report['issues']}
    if not report['mechanically_valid']:
        return {**base, 'status': 'awaiting_external_feedback', 'revision_candidates': [], 'reader_metrics': None}
    pair_errors = []
    for truth, guesses in report['confusion'].items():
        for guess, n in guesses.items():
            if truth != guess and n:
                pair_errors.append({'true_role': truth, 'guessed_role': guess, 'confusions': n,
                                    'editorial_action': 'Compare blind-card dialogue strategy, syntax and choice under pressure; revise only grounded scene(s).'})
    pair_errors.sort(key=lambda x: (-x['confusions'], x['true_role'], x['guessed_role']))
    return {**base, 'status': 'editorial_triage_required', 'reader_metrics': {'accuracy': report['accuracy'], 'baseline': report['majority_class_baseline']},
            'revision_candidates': pair_errors, 'next_step': 'Human editor examines answer-isolated excerpts; after revision generate fresh cards and recruit an independent follow-up panel.'}


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='mode', required=True)
    a = sub.add_parser('emotion'); a.add_argument('script'); a.add_argument('ledger'); a.add_argument('panel')
    b = sub.add_parser('voice'); b.add_argument('blind'); b.add_argument('key'); b.add_argument('panel')
    for x in (a,b): x.add_argument('--output', required=True)
    args = p.parse_args()
    if args.mode == 'emotion':
        result = triage_emotion(Path(args.script).read_bytes(), *[json.loads(Path(p).read_text(encoding='utf-8')) for p in (args.ledger, args.panel)])
    else:
        result = triage_voice(*[json.loads(Path(p).read_text(encoding='utf-8')) for p in (args.blind, args.key, args.panel)])
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(result['status'])
    return 0 if result['status'] == 'editorial_triage_required' else 2

if __name__ == '__main__':
    raise SystemExit(main())
