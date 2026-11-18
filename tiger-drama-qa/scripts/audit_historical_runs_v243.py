"""Strict preflight for historical-version A/B evidence. Does not run a model."""
import hashlib,json,sys
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(data):
    if data.get('evidence_type') in ('DEMO_ONLY','illustrative'):
        return {'status':'DEMO_ONLY','errors':[]}
    runs=data.get('runs')
    if not isinstance(runs,list) or len(runs)!=2 or any(not isinstance(r,dict) for r in runs):
        return {'status':'NOT_RUN','errors':['exactly two independent run records required']}
    errors=[]
    required=('run_id','version','skill_zip','skill_sha256','source_file','source_sha256','assets_sha256','settings','run_log','output_file','output_sha256')
    for i,r in enumerate(runs):
        for field in required:
            if r.get(field) is None or r.get(field)=='':errors.append(f'run {i}: missing {field}')
        for filefield,hashfield in (('skill_zip','skill_sha256'),('source_file','source_sha256'),('output_file','output_sha256')):
            path=r.get(filefield)
            if not path:continue
            p=Path(path)
            if not p.is_file():errors.append(f'run {i}: missing {filefield}')
            elif digest(p)!=r.get(hashfield):errors.append(f'run {i}: hash mismatch {filefield}')
        log=r.get('run_log')
        if log and (not Path(log).is_file() or not Path(log).read_text(encoding='utf-8').strip()):
            errors.append(f'run {i}: missing or empty log')
    a,b=runs
    for field in ('source_sha256','assets_sha256','settings'):
        if a.get(field)!=b.get(field):errors.append(f'mismatched {field}')
    for field in ('run_id','skill_sha256','run_log','output_file'):
        if a.get(field)==b.get(field):errors.append(f'non-independent {field}')
    if sorted([a.get('version'),b.get('version')])!=['2.38','2.39']:
        errors.append('expected historical versions 2.38 and 2.39')
    if errors:return {'status':'INCOMPARABLE','errors':errors}
    if not all(r.get('provenance_verified') is True for r in runs):
        return {'status':'UNVERIFIED_PROVENANCE','errors':['independent model-run provenance not verified']}
    return {'status':'STRUCTURE_ONLY','errors':[],'note':'Evidence preflight only; not an artistic winner'}

if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))
