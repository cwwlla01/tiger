"""V2.41 evidence-backed scene comparison. Never treats a demo as a real run."""
import json,sys,hashlib
from pathlib import Path

def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(d):
    if d.get('mode')=='demo':
        return {'status':'DEMO_ONLY','errors':[],'note':'Illustrative storyboards are not independent model runs'}
    runs=[d.get('baseline'),d.get('candidate')]
    if any(not isinstance(x,dict) for x in runs):
        return {'status':'NOT_RUN','errors':['Two independent run records required']}
    errors=[]
    for label,run in zip(('baseline','candidate'),runs):
        for field in ('run_id','scene_id','source_hash','asset_hash','conditions','skill_hash','output_hash','source_file','skill_file','output_file','run_log_file'):
            if not run.get(field):errors.append(f'{label}: missing {field}')
        for field,expected in (('source_file','source_hash'),('skill_file','skill_hash'),('output_file','output_hash')):
            file=run.get(field)
            if not file:continue
            p=Path(file)
            if not p.is_file():errors.append(f'{label}: missing file {field}')
            elif sha_file(p)!=run.get(expected):errors.append(f'{label}: hash mismatch {field}')
        log=run.get('run_log_file')
        if log and (not Path(log).is_file() or not Path(log).read_text(encoding='utf-8').strip()):
            errors.append(f'{label}: absent run log')
    a,b=runs
    for field in ('scene_id','source_hash','asset_hash','conditions'):
        if a.get(field)!=b.get(field):errors.append(f'mismatch {field}')
    for field in ('run_id','skill_hash','output_hash','run_log_file'):
        if a.get(field)==b.get(field):errors.append(f'not distinct {field}')
    if errors:return {'status':'INCOMPARABLE','errors':errors}
    return {'status':'STRUCTURE_ONLY','errors':[],'note':'File evidence consistent; human blind review and creative provenance still require independent verification'}

if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))
