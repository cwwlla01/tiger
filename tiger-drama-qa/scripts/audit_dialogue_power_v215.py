"""Structural dialogue-power handoff checks; not creative/video QA."""

def audit(bundle):
    errors=[]
    stages=bundle.get('stages',{})
    director=stages.get('03',{}).get('takes',[])
    ids=[t.get('take_id') for t in director]
    if len(ids)!=len(set(ids)): errors.append('DUPLICATE_TAKE_ID')
    by_id={t.get('take_id'):t for t in director}
    for t in director:
        tid=t.get('take_id'); dp=t.get('dialogue_power')
        if not dp: continue
        beats=dp.get('beats',[])
        if not beats: errors.append(f'{tid}:NO_DIALOGUE_BEATS')
        beat_ids=[b.get('beat_id') for b in beats]
        if any(not x for x in beat_ids) or len(beat_ids)!=len(set(beat_ids)): errors.append(f'{tid}:INVALID_BEAT_IDS')
        for b in beats:
            for field in ('source_anchor','speaker_id','listener_ids','line_or_silence','eyeline_target','screen_axis','knowledge_after'):
                if b.get(field) is None or b.get(field)=='': errors.append(f'{tid}:{b.get("beat_id")}:MISSING_{field}')
            if b.get('speaker_id') in b.get('listener_ids',[]): errors.append(f'{tid}:{b.get("beat_id")}:SELF_LISTENER')
    for stage in ('04','05'):
        for t in stages.get(stage,{}).get('takes',[]):
            tid=t.get('take_id')
            if tid not in by_id: errors.append(f'{stage}:{tid}:UNKNOWN_TAKE');continue
            src=by_id[tid].get('dialogue_power')
            if not src: continue
            dst=t.get('dialogue_power')
            if not dst: errors.append(f'{stage}:{tid}:MISSING_DIALOGUE_POWER');continue
            orig=src.get('beats',[]); now=dst.get('beats',[])
            om={b['beat_id']:b for b in orig if b.get('beat_id')}
            order=[b.get('beat_id') for b in now]
            expected=[b.get('beat_id') for b in orig]
            if stage=='05' and order!=expected: errors.append(f'{stage}:{tid}:BEAT_ORDER_DRIFT')
            if stage=='04' and any(x not in expected for x in order): errors.append(f'{stage}:{tid}:INVENTED_FRAME_BEAT')
            for b in now:
                bid=b.get('beat_id')
                if bid not in om: errors.append(f'{stage}:{tid}:{bid}:UNKNOWN_BEAT');continue
                for field in ('speaker_id','listener_ids','line_or_silence','eyeline_target','screen_axis','knowledge_after'):
                    if b.get(field)!=om[bid].get(field): errors.append(f'{stage}:{tid}:{bid}:{field.upper()}_DRIFT')
    return errors
