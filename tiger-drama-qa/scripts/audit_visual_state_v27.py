#!/usr/bin/env python3
"""V2.7 canonical visual-state handoff validator (structural, not media QA)."""
import argparse
import json
from pathlib import Path

STAGES = ('03', '04', '05')
IMMUTABLE = ('series_look_ref', 'scene_look_ref', 'character_asset_ref', 'material_ref',
             'world_light_refs', 'camera', 'composition', 'palette', 'weather',
             'motion', 'face_light_claims')


def audit(bundle):
    errors = []
    stages = bundle.get('stages', {})
    for stage in STAGES:
        if stage not in stages or not isinstance(stages[stage], dict):
            errors.append(f'missing/invalid stage {stage}')
    if errors:
        return errors
    source = stages['03']
    for stage in STAGES:
        entries = stages[stage].get('takes', [])
        if not isinstance(entries, list):
            errors.append(f'{stage}: takes must be array')
            continue
        ids = [x.get('take_id') for x in entries if isinstance(x, dict)]
        if len(ids) != len(entries) or any(not x for x in ids) or len(ids) != len(set(ids)):
            errors.append(f'{stage}: invalid or duplicate take IDs')
    if errors:
        return errors
    originals = {x['take_id']: x for x in source['takes']}
    if not originals:
        errors.append('03: no takes')
    for stage in ('04', '05'):
        targets = {x['take_id']: x for x in stages[stage]['takes']}
        for tid in originals.keys() - targets.keys():
            errors.append(f'{tid}: missing {stage} take')
        for tid in targets.keys() - originals.keys():
            errors.append(f'{tid}: {stage} take has no 03 source')
        for tid in originals.keys() & targets.keys():
            base, target = originals[tid], targets[tid]
            for field in IMMUTABLE:
                if field in base and target.get(field) != base[field]:
                    errors.append(f'{tid}: {stage} changed/missing {field}')
            if target.get('director_revision_required'):
                errors.append(f'{tid}: {stage} requires director revision')
    for take in source['takes']:
        tid = take['take_id']
        for field in ('series_look_ref', 'scene_look_ref', 'camera', 'composition'):
            if not take.get(field):
                errors.append(f'{tid}: 03 missing {field}')
        for claim in take.get('face_light_claims', []):
            if claim.get('light_id') not in take.get('world_light_refs', []):
                errors.append(f'{tid}: face light claim references undeclared light')
    return sorted(errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle')
    args = parser.parse_args()
    errors = audit(json.loads(Path(args.bundle).read_text(encoding='utf-8')))
    print(json.dumps({'passed': not errors, 'errors': errors,
                      'scope': 'structured 03/04/05 handoff only; no rendered media verification'},
                     ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
