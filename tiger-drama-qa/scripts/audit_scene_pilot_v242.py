#!/usr/bin/env python3
"""V2.42 illustrative scene draft structure audit. Never establishes real Skill A/B superiority."""
import json,sys
from pathlib import Path

def audit(data):
    errors=[]
    beats=data.get('beats',[])
    beat_ids=[b.get('id') for b in beats]
    if not beat_ids or len(beat_ids)!=len(set(beat_ids)) or any(not x for x in beat_ids):errors.append('invalid_frozen_beats')
    candidates=data.get('candidates',[])
    if len(candidates)!=2 or len({c.get('id') for c in candidates})!=2:errors.append('requires_two_distinct_candidates')
    metrics=[]
    for c in candidates:
        shots=c.get('shots',[]); seen=set(); covered=set(); total=0
        if not shots:errors.append(f"{c.get('id')}:empty_shots")
        for s in shots:
            sid=s.get('shot_id');ids=s.get('beat_ids',[])
            if not sid or sid in seen:errors.append(f"{c.get('id')}:duplicate_or_missing_shot_id")
            seen.add(sid)
            if not ids or any(b not in beat_ids for b in ids):errors.append(f"{c.get('id')}:{sid}:unknown_or_empty_beat")
            covered.update(ids)
            if not s.get('dramatic_function') or not s.get('editorial_reason'):errors.append(f"{c.get('id')}:{sid}:missing_editorial_reason")
            if not s.get('camera') or not s.get('sound'):errors.append(f"{c.get('id')}:{sid}:missing_execution")
            d=s.get('duration_s')
            if isinstance(d,bool) or not isinstance(d,(int,float)) or not 0<d<=120:errors.append(f"{c.get('id')}:{sid}:invalid_duration")
            else:total+=d
        missing=set(beat_ids)-covered
        if missing:errors.append(f"{c.get('id')}:missing_beats:{','.join(sorted(missing))}")
        metrics.append({'candidate':c.get('id'),'shot_count':len(shots),'duration_s':total,'covered_beats':len(covered & set(beat_ids))})
    # The fixture can only establish a demonstration, regardless of metadata.
    return {'status':'INVALID' if errors else 'DEMO_ONLY','errors':errors,'metrics':metrics,'artistic_winner':None,'real_version_ab_proven':False}

if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))
