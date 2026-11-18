#!/usr/bin/env python3
"""V2.45 historical A/B evidence gate; does not judge artistic merit."""
import argparse, hashlib, json
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(manifest_path, scene_path, runs_root):
    manifest=json.loads(Path(manifest_path).read_text())
    if digest(scene_path)!=manifest['scene_sha256']:
        return {'status':'INCOMPARABLE','errors':['FROZEN_SCENE_HASH_MISMATCH']}
    errors=[]; ids=set(); arms=manifest['arms']; complete=0
    for arm in arms:
        root=Path(runs_root)/arm['arm'].replace('.','').lower()
        log=root/'run.json'; output=root/'03-专业导演分镜.md'
        if not log.exists() or not output.exists():
            errors.append(f"{arm['arm']}:MISSING_RUN_ARTIFACT"); continue
        try: record=json.loads(log.read_text())
        except (ValueError,UnicodeError):
            errors.append(f"{arm['arm']}:INVALID_RUN_LOG"); continue
        complete+=1
        for key,expected in [('arm',arm['arm']),('source_zip_sha256',arm['source_zip_sha256']),('scene_sha256',manifest['scene_sha256']),('output_sha256',digest(output))]:
            if record.get(key)!=expected: errors.append(f"{arm['arm']}:{key.upper()}_MISMATCH")
        for key in ('run_id','timestamp','model','settings'):
            if not record.get(key): errors.append(f"{arm['arm']}:MISSING_{key.upper()}")
        if record.get('independence_attested') is not True: errors.append(f"{arm['arm']}:INDEPENDENCE_NOT_ATTESTED")
        rid=record.get('run_id')
        if rid in ids: errors.append('DUPLICATE_RUN_ID')
        ids.add(rid)
        if not output.read_text().strip(): errors.append(f"{arm['arm']}:EMPTY_OUTPUT")
    if complete==0: status='NOT_RUN'
    elif errors: status='INCOMPARABLE'
    else: status='STRUCTURE_ONLY'
    return {'status':status,'errors':errors,'completed_arms':complete,'total_arms':len(arms),'artistic_superiority_proven':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('scene');p.add_argument('runs_root');a=p.parse_args()
    print(json.dumps(audit(a.manifest,a.scene,a.runs_root),ensure_ascii=False,indent=2))
