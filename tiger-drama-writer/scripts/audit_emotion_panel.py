#!/usr/bin/env python3
"""Check provenance and completeness of independently collected emotional-response ratings.

A mechanically valid panel is not proof of real humans or artistic quality.
"""
import argparse
import hashlib
import json
from pathlib import Path

DIMENSIONS = ('choice_credibility', 'consequence_clarity', 'relationship_change', 'emotional_impact')


def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def audit(script_bytes, ledger, panel, min_readers=3):
    problems = []
    script_sha = hashlib.sha256(script_bytes).hexdigest()
    ledger_sha = fingerprint(ledger)
    if ledger.get('script_sha256') != script_sha:
        problems.append('ledger is not bound to supplied script')
    if panel.get('script_sha256') != script_sha or panel.get('ledger_sha256') != ledger_sha:
        problems.append('panel script/ledger hash mismatch')
    if panel.get('status') != 'completed':
        problems.append('no completed external panel')
    readers = panel.get('readers', [])
    if not isinstance(readers, list):
        problems.append('readers must be a list')
        readers = []
    if len(readers) < min_readers:
        problems.append('insufficient independent readers')
    ids, evidence = [], []
    scores = {d: [] for d in DIMENSIONS}
    for item in readers:
        if not isinstance(item, dict):
            problems.append('malformed reader'); continue
        rid = item.get('reader_id')
        if not isinstance(rid, str) or len(rid.strip()) < 3:
            problems.append('missing reader id')
        else:
            ids.append(rid.strip())
        ref = item.get('evidence_ref')
        if not isinstance(ref, str) or len(ref.strip()) < 4 or not item.get('collected_by'):
            problems.append(f'missing independent collection evidence for {rid}')
        else:
            evidence.append(ref.strip())
        ratings = item.get('ratings')
        if not isinstance(ratings, dict) or set(ratings) != set(DIMENSIONS):
            problems.append(f'incomplete dimensions for {rid}'); continue
        for dim in DIMENSIONS:
            rating = ratings[dim]
            if type(rating) is not int or not 1 <= rating <= 5:
                problems.append(f'invalid rating {dim} for {rid}')
            else:
                scores[dim].append(rating)
        for key in ('most_effective_moment', 'least_convincing_moment', 'reason'):
            val = item.get(key)
            if not isinstance(val, str) or len(val.strip()) < 8:
                problems.append(f'missing qualitative response {key} for {rid}')
    if len(ids) != len(set(ids)):
        problems.append('duplicate reader ids')
    if len(evidence) != len(set(evidence)):
        problems.append('reused collection evidence')
    valid = not problems
    return {'mechanically_valid': valid, 'independent_people_verified': False,
            'artistic_quality_certified': False, 'script_sha256': script_sha,
            'ledger_sha256': ledger_sha, 'reader_count': len(readers),
            'rating_means': {d: round(sum(scores[d])/len(scores[d]), 2) for d in DIMENSIONS} if valid else None,
            'ratings_by_dimension': scores if valid else None,
            'issues': problems,
            'conclusion': ('Externally supplied rating records internally consistent; real participants and artistic merits require independent verification.'
                           if valid else 'NOT TESTED / INCOMPLETE; no defensible reader ratings.')}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('script'); p.add_argument('ledger'); p.add_argument('panel'); p.add_argument('--output', required=True)
    a = p.parse_args()
    result = audit(Path(a.script).read_bytes(), json.loads(Path(a.ledger).read_text(encoding='utf-8')),
                   json.loads(Path(a.panel).read_text(encoding='utf-8')))
    Path(a.output).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'mechanically_valid': result['mechanically_valid'], 'issues': result['issues']}, ensure_ascii=False))
    return 0 if result['mechanically_valid'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
