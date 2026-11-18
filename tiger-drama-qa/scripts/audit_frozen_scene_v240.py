"""V2.40 frozen-scene evidence and beat coverage audit; does not judge artistry."""
import json,sys,hashlib
from pathlib import Path

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit(d):
    a,b=d.get('baseline'),d.get('candidate')
    if not isinstance(a,dict) or not isinstance(b,dict):
        return {'status':'NOT_RUN','errors':['Both independent run records required']}
    errors=[]
    beats=d.get('frozen_beats')
    if not isinstance(beats,list) or not beats or any(not isinstance(x,str) or not x for x in beats) or len(beats)!=len(set(beats)):
        errors.append('Invalid frozen beats')
        beats=[]
    for label,run in [('baseline',a),('candidate',b)]:
        for field in ('run_id','scene_id','source_hash','asset_hash','skill_hash','conditions','shots','output_hash'):
            if not run.get(field):errors.append(f'{label}: missing {field}')
        shots=run.get('shots')
        if not isinstance(shots,list) or not shots:
            errors.append(f'{label}: missing full shot records');continue
        ids=[];covered=set()
        for shot in shots:
            if not isinstance(shot,dict):errors.append(f'{label}: malformed shot');continue
            for field in ('shot_id','source_beat_id','description','dramatic_function','cut_trigger'):
                if not shot.get(field):errors.append(f'{label}: missing shot {field}')
            ids.append(shot.get('shot_id'))
            sb=shot.get('source_beat_id')
            if isinstance(sb,str):covered.add(sb)
            else:errors.append(f'{label}: invalid source_beat_id')
        if len(ids)!=len(set(ids)):errors.append(f'{label}: duplicate shot_id')
        if set(beats)-covered:errors.append(f'{label}: missing beats {sorted(set(beats)-covered)}')
        if covered-set(beats):errors.append(f'{label}: unknown beats {sorted(covered-set(beats))}')
        if run.get('output_hash')!=digest(shots):errors.append(f'{label}: output hash mismatch')
    if a.get('run_id')==b.get('run_id'):errors.append('Runs not independent')
    for field in ('scene_id','source_hash','asset_hash','conditions'):
        if a.get(field)!=b.get(field):errors.append(f'Mismatched {field}')
    if a.get('skill_hash')==b.get('skill_hash'):errors.append('Skill versions not distinct')
    if a.get('output_hash')==b.get('output_hash'):errors.append('Outputs identical')
    if errors:return {'status':'INCOMPARABLE','errors':errors}
    review=d.get('blind_review')
    if not isinstance(review,dict) or not review.get('independent') or not review.get('reviewer_id') or not review.get('scores') or not review.get('rationale'):
        return {'status':'STRUCTURE_ONLY','errors':[],'note':'Independent human blind review not evidenced'}
    return {'status':'REVIEW_RECORDED_NOT_ART_PROVEN','errors':[],'note':'Review metadata exists; no automatic artistic superiority conclusion'}

if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))
