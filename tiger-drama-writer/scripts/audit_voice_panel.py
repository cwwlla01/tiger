#!/usr/bin/env python3
"""Validate externally collected blind role-identification replies; never invent readers."""
import argparse
import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


def audit(blind, key, panel, min_readers=3):
    problems = []
    cards = blind.get('cards', [])
    ids = [c.get('id') for c in cards]
    roles = blind.get('candidate_roles', [])
    if not ids or len(ids) != len(set(ids)) or not roles or len(roles) != len(set(roles)):
        problems.append('invalid blind cards or candidate roles')
    if set(key) != set(ids) or any(key.get(i, {}).get('role') not in roles for i in ids):
        problems.append('answer key inconsistent with blind cards')
    expected_fingerprint = hashlib.sha256(json.dumps(blind, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if panel.get('blind_sha256') != expected_fingerprint:
        problems.append('blind pack hash mismatch')
    if panel.get('status') != 'completed':
        problems.append('no completed external reader panel')
    readers = panel.get('readers', [])
    if not isinstance(readers, list):
        readers = []
        problems.append('readers must be a list')
    if len(readers) < min_readers:
        problems.append('insufficient readers')
    reader_ids = [r.get('reader_id') for r in readers if isinstance(r, dict)]
    if len(reader_ids) != len(set(reader_ids)) or any(not isinstance(x, str) or len(x.strip()) < 3 for x in reader_ids):
        problems.append('reader identifiers must be nonempty and unique')
    if any('answer key' in p for p in problems):
        return {'mechanically_valid': False, 'independent_people_verified': False, 'accuracy': None, 'issues': problems, 'conclusion': 'NOT TESTED / INCOMPLETE — invalid key.'}
    confusion = defaultdict(Counter)
    correct = 0
    total = 0
    per_reader = []
    for reader in readers:
        if not isinstance(reader, dict):
            problems.append('invalid reader record')
            continue
        rid = reader.get('reader_id')
        answers = reader.get('answers')
        if not isinstance(answers, dict) or set(answers) != set(ids) or any(a not in roles for a in answers.values()):
            problems.append(f'incomplete/invalid answers: {rid}')
            continue
        if not reader.get('collected_by') or not reader.get('evidence_ref'):
            problems.append(f'missing external collection evidence: {rid}')
            continue
        local = 0
        for card_id in ids:
            truth = key[card_id]['role']
            guess = answers[card_id]
            confusion[truth][guess] += 1
            local += guess == truth
        correct += local
        total += len(ids)
        per_reader.append({'reader_id': rid, 'correct': local, 'total': len(ids), 'accuracy': round(local / len(ids), 4)})
    if len(per_reader) != len(readers):
        problems.append('invalid reader replies')
    counts = Counter(key[i]['role'] for i in ids) if not problems or not any('answer key' in p for p in problems) else Counter()
    baseline = max(counts.values()) / len(ids) if ids and counts else None
    return {'mechanically_valid': not problems, 'independent_people_verified': False,
            'source_sha256': blind.get('source_sha256'), 'blind_sha256': expected_fingerprint,
            'reader_count': len(readers), 'cards': len(ids), 'scored_responses': total,
            'accuracy': round(correct / total, 4) if total and not problems else None,
            'majority_class_baseline': round(baseline, 4) if baseline is not None else None,
            'per_reader': per_reader if not problems else [],
            'confusion': {r: dict(c) for r, c in confusion.items()} if not problems else {},
            'issues': problems,
            'conclusion': 'Mechanically validated external responses; reader identity and artistic quality NOT verified.' if not problems else 'NOT TESTED / INCOMPLETE — no valid independent voice result.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('blind'); ap.add_argument('key'); ap.add_argument('panel')
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    blind, key, panel = [json.loads(Path(p).read_text(encoding='utf-8')) for p in (args.blind, args.key, args.panel)]
    result = audit(blind, key, panel)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'mechanically_valid': result['mechanically_valid'], 'issues': result['issues'], 'accuracy': result['accuracy']}, ensure_ascii=False))
    raise SystemExit(0 if result['mechanically_valid'] else 2)

if __name__ == '__main__':
    main()
