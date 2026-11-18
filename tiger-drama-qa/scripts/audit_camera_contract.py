#!/usr/bin/env python3
"""Compare structured 03/05 camera handoff manifests; does not assess rendered videos."""
import argparse
import json
from pathlib import Path

SPECIAL = {
    'CAM-12': {'orbit_direction', 'height_change', 'subject_anchor'},
    'CAM-21': {'whip_direction', 'start_target', 'end_target'},
    'CAM-22': {'dolly_direction', 'zoom_direction', 'subject_size_lock'},
    'CAM-31': {'freeze_behavior', 'viewpoint_motion', 'implementation_route'},
}


def audit(director, video):
    errors = []
    ds = {s['take_id']: s for s in director['takes']}
    vs = {s['take_id']: s for s in video['takes']}
    for take_id, shot in ds.items():
        if take_id not in vs:
            errors.append(f'{take_id}: missing 05 take')
            continue
        out = vs[take_id]
        ids = [shot.get('camera_primary_id')] + shot.get('camera_modifier_ids', [])
        if shot.get('camera_primary_id') != out.get('camera_primary_id'):
            errors.append(f'{take_id}: primary camera technique changed')
        for technique in ids:
            if technique and technique not in ([out.get('camera_primary_id')] + out.get('camera_modifier_ids', [])):
                errors.append(f'{take_id}: technique {technique} missing from 05')
            for field in SPECIAL.get(technique, ()):
                if not shot.get(field):
                    errors.append(f'{take_id}: 03 missing {field} for {technique}')
                elif out.get(field) != shot.get(field):
                    errors.append(f'{take_id}: 05 changed/missing {field} for {technique}')
        for field in ('start_state', 'end_state', 'screen_axis'):
            if shot.get(field) and shot.get(field) != out.get(field):
                errors.append(f'{take_id}: 05 changed/missing {field}')
        if shot.get('director_revision_required') and not out.get('director_revision_required'):
            errors.append(f'{take_id}: unapproved director revision not flagged')
    for take_id in vs.keys() - ds.keys():
        errors.append(f'{take_id}: 05 take has no 03 source')
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--director-json', required=True)
    p.add_argument('--video-json', required=True)
    args = p.parse_args()
    errors = audit(json.loads(Path(args.director_json).read_text(encoding='utf-8')),
                   json.loads(Path(args.video_json).read_text(encoding='utf-8')))
    if errors:
        print('CAMERA CONTRACT FAIL:\n' + '\n'.join(errors))
        return 1
    print('CAMERA CONTRACT PASS: structured handoff only; video output not verified')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
