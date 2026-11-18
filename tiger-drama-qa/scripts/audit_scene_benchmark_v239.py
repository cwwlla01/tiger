"""V2.39 independent scene benchmark evidence audit. JSON in, JSON out."""
import hashlib
import json
import sys
from pathlib import Path

REQUIRED = ('run_id','source_hash','skill_hash','output_hash','scene_id','shots')

def audit(data):
    errors=[]
    a,b=data.get('baseline'),data.get('candidate')
    if not isinstance(a,dict) or not isinstance(b,dict):
        return {'status':'NOT_RUN','errors':['Missing independent baseline or candidate run']}
    for name,run in (('baseline',a),('candidate',b)):
        for key in REQUIRED:
            if not run.get(key):errors.append(f'{name}: missing {key}')
        shots=run.get('shots')
        if not isinstance(shots,list) or not shots:errors.append(f'{name}: no full shot evidence')
        else:
            ids=[s.get('shot_id') for s in shots if isinstance(s,dict)]
            if len(ids)!=len(shots) or not all(ids) or len(ids)!=len(set(ids)):
                errors.append(f'{name}: invalid or duplicate shot ids')
            if any(not isinstance(s,dict) or not s.get('description') or not s.get('source_beat_id') for s in shots):
                errors.append(f'{name}: missing shot descriptions or source beats')
    if a.get('run_id')==b.get('run_id'):errors.append('Runs must be independent')
    if a.get('source_hash')!=b.get('source_hash'):errors.append('Different source inputs')
    if a.get('scene_id')!=b.get('scene_id'):errors.append('Different scenes')
    if a.get('skill_hash')==b.get('skill_hash'):errors.append('Same Skill version; not a version comparison')
    if a.get('output_hash')==b.get('output_hash'):errors.append('Identical output artifacts')
    if a.get('asset_hash')!=b.get('asset_hash'):errors.append('Different asset versions')
    if a.get('conditions')!=b.get('conditions'):errors.append('Different generation conditions')
    if errors:return {'status':'INCOMPARABLE','errors':errors}
    review=data.get('blind_review')
    if not isinstance(review,dict) or not review.get('reviewer_id') or not review.get('independent') or not review.get('scores'):
        return {'status':'STRUCTURE_ONLY','errors':[],'note':'No documented independent blind review; no artistic superiority claim'}
    return {'status':'REVIEW_RECORDED_NOT_ART_PROVEN','errors':[],'note':'Review metadata recorded; inspect actual judgments before making claims'}

def main():
    data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print(json.dumps(audit(data),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
