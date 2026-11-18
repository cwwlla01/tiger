#!/usr/bin/env python3
"""Audit structured 03/04/05 visual handoff. Text-level only; not rendered media QA."""
import argparse
import json
from pathlib import Path

FIELDS = ('series_look_ref', 'scene_look_ref', 'character_asset_ref', 'material_ref',
          'key_light_source', 'key_light_direction', 'weather', 'palette',
          'screen_direction', 'composition', 'focus_target')
REQUIRED = ('take_id', 'series_look_ref', 'scene_look_ref', 'key_light_source',
            'key_light_direction', 'composition', 'screen_direction')


def audit(director, still, video):
    errors = []
    groups = {}
    for label, manifest in (('03', director), ('04', still), ('05', video)):
        shots = manifest.get('takes', [])
        ids = [s.get('take_id') for s in shots]
        if len(ids) != len(set(ids)):
            errors.append(f'{label}: duplicate take_id')
        groups[label] = {s.get('take_id'): s for s in shots}
    for take_id, shot in groups['03'].items():
        for field in REQUIRED:
            if not shot.get(field):
                errors.append(f'{take_id}: 03 missing {field}')
        for label in ('04', '05'):
            other = groups[label].get(take_id)
            if other is None:
                errors.append(f'{take_id}: missing {label} take')
                continue
            for field in FIELDS:
                if field in shot and shot[field] != other.get(field):
                    errors.append(f'{take_id}: {label} changed/missing {field}')
        for label in ('04', '05'):
            other = groups[label].get(take_id, {})
            if other.get('composition_rules') and len(set(other['composition_rules'])) > 1:
                if {'center', 'thirds', 'symmetry'} <= set(other['composition_rules']):
                    errors.append(f'{take_id}: {label} conflicting composition rules')
        for label in ('04', '05'):
            other = groups[label].get(take_id, {})
            if other.get('unapproved_visual_change'):
                errors.append(f'{take_id}: {label} unapproved visual change')
    for label in ('04', '05'):
        for extra in groups[label].keys() - groups['03'].keys():
            errors.append(f'{extra}: {label} take has no 03 source')
    # Check adjacent shots in same scene: light/weather changes require explicit motivation.
    ordered = director.get('takes', [])
    for prev, curr in zip(ordered, ordered[1:]):
        if prev.get('scene_id') != curr.get('scene_id'):
            continue
        for field in ('key_light_source', 'weather'):
            if prev.get(field) != curr.get(field) and not curr.get('continuity_change_reason'):
                errors.append(f"{curr.get('take_id')}: unexplained {field} change from prior take")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('director', 'still', 'video'):
        parser.add_argument(f'--{key}-json', required=True)
    args = parser.parse_args()
    manifests = [json.loads(Path(getattr(args, f'{key}_json')).read_text(encoding='utf-8'))
                 for key in ('director', 'still', 'video')]
    errors = audit(*manifests)
    if errors:
        print('VISUAL CONTRACT FAIL:\n' + '\n'.join(errors))
        return 1
    print('VISUAL CONTRACT PASS (structured text only; media NOT_VERIFIED)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
