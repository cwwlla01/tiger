#!/usr/bin/env python3
"""Validate a screenplay project manifest, versions, canon, and local point arithmetic."""
import json
import sys
from pathlib import Path

REQUIRED = ['project.json', 'canon.json', 'episodes.json', 'progression.json', 'open_threads.json', 'changes.json']
STATUS = {'OUTLINE', 'SCENE_DRAFT', 'FULL_SCRIPT', 'TIMED'}
SOURCE = {'USER_LOCKED', 'APPROVED_DRAFT', 'DERIVED', 'PROPOSED'}

def main(folder):
    root = Path(folder)
    errors, warnings = [], []
    data = {}
    for name in REQUIRED:
        p = root / name
        if not p.exists():
            errors.append(f'Missing {name}')
            continue
        try:
            data[name] = json.loads(p.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f'Cannot read {name}: {e}')
    if errors:
        return errors, warnings
    canon = data['canon.json']
    seen = set()
    for c in canon:
        if c.get('id') in seen: errors.append('Duplicate canon ID: ' + str(c.get('id')))
        seen.add(c.get('id'))
        if c.get('source') not in SOURCE: errors.append('Invalid canon source: ' + str(c.get('id')))
        if c.get('source') == 'USER_LOCKED' and not c.get('evidence'):
            errors.append('User locked fact missing evidence: ' + str(c.get('id')))
    episodes = data['episodes.json']
    ids = set()
    for e in episodes:
        key = (e.get('episode'), e.get('revision'))
        if key in ids: errors.append('Duplicate episode revision: ' + str(key))
        ids.add(key)
        if e.get('status') not in STATUS: errors.append('Invalid script status: ' + str(key))
        if e.get('approval') == 'APPROVED' and not e.get('approval_evidence'):
            errors.append('Approval missing evidence: ' + str(key))
        if e.get('file') and not (root / e['file']).exists():
            warnings.append('Unattached script reference: ' + str(e['file']))
    for t in data['progression.json']:
        earned = t.get('earned')
        spend = t.get('spend', {})
        if earned is not None and any(not isinstance(n,(int,float)) or n < 0 for n in spend.values()):
            errors.append('Invalid allocation: ' + str(t.get('id')))
        if earned is not None and sum(spend.values()) > earned + t.get('prior_balance', 0):
            errors.append('Insufficient points in transaction: ' + str(t.get('id')))
        if earned is None: warnings.append('Unreconciled point source: ' + str(t.get('id')))
    if data['project.json'].get('ledger_reconciled') is False:
        warnings.append('Overall progression ledger intentionally unreconciled')
    return errors, warnings

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit('Usage: check_project.py <project_directory>')
    err, warn = main(sys.argv[1])
    for msg in err: print('ERROR:', msg)
    for msg in warn: print('WARNING:', msg)
    print('PASS' if not err else 'FAIL')
    sys.exit(1 if err else 0)
