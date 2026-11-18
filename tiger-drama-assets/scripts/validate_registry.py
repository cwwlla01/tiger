#!/usr/bin/env python3
"""Static checks for the asset registry and director handoff JSON. No image or approval verification."""
import argparse
import json
from pathlib import Path

CATS = {'CHAR', 'PROP', 'SCENE', 'MONSTER'}
APPROVAL = {'PROPOSED', 'QC_PASSED', 'APPROVED', 'REJECTED', 'CONFLICT'}
HISTORY = {'VERIFIED', 'PARTIAL', 'REGISTRY_UNAVAILABLE', 'HISTORY_NOT_VERIFIED'}
PRIORITY = {'BLOCKING', 'HIGH', 'NORMAL', 'OPTIONAL'}

def check(reg, handoff=None):
    errors = []
    def err(msg): errors.append(msg)
    if not reg.get('project_id') or reg['project_id'] == 'PROJECT_ID_REQUIRED': err('project_id missing')
    if reg.get('history_status') not in HISTORY: err('invalid history_status')
    known = set()
    stages = {}
    looks = {}
    for individual in reg.get('individuals', []):
        ident = individual.get('individual_id')
        if not ident or ident in known: err(f'duplicate/empty individual_id: {ident}')
        known.add(ident)
        if individual.get('category') not in CATS: err(f'{ident}: invalid category')
        stage_ids = set()
        for stage in individual.get('stages', []):
            sid = stage.get('stage_id')
            if not sid or sid in stage_ids: err(f'{ident}: duplicate/empty stage_id {sid}')
            stage_ids.add(sid)
            look_ids = set()
            for look in stage.get('looks', []):
                lid = look.get('look_id')
                if not lid or lid in look_ids: err(f'{ident}/{sid}: duplicate/empty look_id {lid}')
                look_ids.add(lid)
                if look.get('approval_status') not in APPROVAL: err(f'{ident}/{sid}/{lid}: invalid approval')
                versions = set()
                for rev in look.get('image_revisions', []):
                    version = rev.get('version')
                    if not version or version in versions: err(f'{ident}/{sid}/{lid}: duplicate/empty version')
                    versions.add(version)
                    if rev.get('approval_status') not in APPROVAL: err(f'{ident}/{sid}/{lid}: invalid revision approval')
                    if rev.get('image_status') == 'IMAGE_VERIFIED' and not rev.get('uri'): err(f'{ident}/{sid}/{lid}: verified image missing uri')
            looks[(ident, sid)] = look_ids
        stages[ident] = stage_ids
    if handoff is not None:
        if handoff.get('project_id') != reg.get('project_id'): err('handoff project mismatch')
        req_ids = set()
        for req in handoff.get('asset_requirements', []):
            rid = req.get('requirement_id')
            if not rid or rid in req_ids: err(f'duplicate/empty requirement_id {rid}')
            req_ids.add(rid)
            if req.get('priority') not in PRIORITY: err(f'{rid}: invalid priority')
            ident = req.get('individual_id')
            if ident and not ident.startswith('TMP-'):
                if ident not in known: err(f'{rid}: unknown individual {ident}')
                elif req.get('stage_id') not in stages.get(ident, set()): err(f'{rid}: unknown stage')
                elif req.get('look_id') not in looks.get((ident, req.get('stage_id')), set()): err(f'{rid}: unknown look')
        for task in handoff.get('production_tasks', []):
            for rid in task.get('requirement_ids', []):
                if rid not in req_ids: err(f"task {task.get('task_id')}: unknown requirement {rid}")
        for binding in handoff.get('resolved_bindings', []):
            if binding.get('requirement_id') not in req_ids: err('binding unknown requirement')
            if binding.get('verification_status') == 'IMAGE_VERIFIED' and not binding.get('image_uri'): err('verified binding missing image_uri')
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument('registry')
    p.add_argument('--handoff')
    a = p.parse_args()
    reg = json.loads(Path(a.registry).read_text(encoding='utf-8'))
    hand = json.loads(Path(a.handoff).read_text(encoding='utf-8')) if a.handoff else None
    issues = check(reg, hand)
    if issues:
        print('FAIL:\n' + '\n'.join('- ' + x for x in issues))
        raise SystemExit(1)
    print('PASS: static structure and references valid (not visual QA or user approval)')
if __name__ == '__main__': main()
