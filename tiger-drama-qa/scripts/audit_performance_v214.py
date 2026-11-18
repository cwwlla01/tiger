"""Structural performance beat handoff audit; not artistic or video QA."""

def audit(bundle):
    errors=[]
    stages=bundle.get('stages',{})
    director=stages.get('03',{}).get('takes',[])
    by_id={t.get('take_id'):t for t in director}
    if len(by_id)!=len(director): errors.append('DUPLICATE_TAKE_ID')
    for take in director:
        tid=take.get('take_id')
        perf=take.get('performance')
        if not perf: continue
        for key in ('source_anchor','character_id','objective','obstacle','knowledge_before','knowledge_after'):
            if not perf.get(key): errors.append(f'{tid}:MISSING_{key}')
        beats=perf.get('beats',[])
        ids=[b.get('beat_id') for b in beats]
        if not beats or any(not x for x in ids) or len(set(ids))!=len(ids): errors.append(f'{tid}:INVALID_BEATS')
        for b in beats:
            if not b.get('observable_action') or not b.get('start_state') or not b.get('end_state'):
                errors.append(f'{tid}:UNOBSERVABLE_BEAT')
    for stage in ('04','05'):
        for take in stages.get(stage,{}).get('takes',[]):
            tid=take.get('take_id')
            if tid not in by_id: errors.append(f'{stage}:{tid}:UNKNOWN_TAKE');continue
            original=by_id[tid].get('performance')
            if original:
                if not take.get('performance'): errors.append(f'{stage}:{tid}:PERFORMANCE_MISSING');continue
                p=take['performance']
                if p.get('character_id')!=original.get('character_id'): errors.append(f'{stage}:{tid}:CHARACTER_DRIFT')
                if p.get('knowledge_after')!=original.get('knowledge_after'): errors.append(f'{stage}:{tid}:KNOWLEDGE_DRIFT')
                src=[b.get('beat_id') for b in original.get('beats',[])]
                dst=[b.get('beat_id') for b in p.get('beats',[])]
                if stage=='05' and src!=dst: errors.append(f'{stage}:{tid}:BEAT_ORDER_DRIFT')
                if stage=='04' and not set(dst).issubset(set(src)): errors.append(f'{stage}:{tid}:FRAME_BEAT_INVENTED')
    return errors
