"""V2.20 structural handoff audit; no artistic/video assertions."""
FIELDS=('from_shot_id','to_shot_id','cut_intent','cut_type','reveal_boundary')
VALID={'STRAIGHT','MATCH_ACTION','EYELINE','SOUND_BRIDGE','ELLIPSIS'}
BRIDGES={'NONE','J_CUT','L_CUT'}
def audit(data):
    errors=[]
    shots=data.get('shot_order',[])
    links=data.get('03',[])
    ids=set()
    for link in links:
        key=link.get('edit_link_id')
        if not key or key in ids: errors.append('duplicate_or_missing_link_id')
        ids.add(key)
        if any(not link.get(f) for f in FIELDS): errors.append('missing_required_field')
        if link.get('cut_type') not in VALID: errors.append('invalid_cut_type')
        a,b=link.get('from_shot_id'),link.get('to_shot_id')
        if a not in shots or b not in shots or shots.index(b)!=shots.index(a)+1: errors.append('nonadjacent_shots')
        if link.get('cut_type')=='MATCH_ACTION' and not (link.get('action_phase_out') and link.get('action_phase_in')): errors.append('missing_action_match')
        if link.get('cut_type')=='EYELINE' and not (link.get('eyeline_source') and link.get('eyeline_target')): errors.append('missing_eyeline')
        if link.get('cut_type')=='SOUND_BRIDGE' and (link.get('sound_bridge') not in {'J_CUT','L_CUT'} or not link.get('sound_source')): errors.append('missing_sound_bridge')
        if link.get('handoff_status') not in {'READY','NEEDS_DIRECTOR_REVIEW','UNVERIFIED'}: errors.append('invalid_handoff_status')
    byid={l.get('edit_link_id'):l for l in links}
    immutable=('from_shot_id','to_shot_id','cut_type','action_phase_out','action_phase_in','screen_direction_out','screen_direction_in','eyeline_source','eyeline_target','sound_bridge','sound_source','reveal_boundary')
    for stage in ('04','05'):
        stage_links=data.get(stage,[])
        stage_ids=[l.get('edit_link_id') for l in stage_links]
        if len(stage_ids)!=len(set(stage_ids)): errors.append(stage+'_duplicate_link')
        if set(stage_ids)!=set(byid): errors.append(stage+'_link_coverage')
        for link in stage_links:
            original=byid.get(link.get('edit_link_id'))
            if original and any(link.get(f)!=original.get(f) for f in immutable): errors.append(stage+'_contract_drift')
    return sorted(set(errors))
