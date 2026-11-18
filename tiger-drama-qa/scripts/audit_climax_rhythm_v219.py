"""Structural 03/04/05 climax handoff audit; not artistic or media verification."""
FIELDS=('sequence_id','beat_id','source_event_ids','dramatic_function','tempo_intent','focus_owner','attention_transition','threat_delta','reversal_trigger','state_before','state_after','cost_paid','result_evidence')
FUNCTIONS={'SETUP','ESCALATE','CHOICE','REVERSAL','PAYOFF','AFTERMATH'}
TEMPOS={'HOLD','BUILD','BURST','RELEASE'}
def audit(data):
    errors=[]; stages=data.get('stages',{})
    indexes={}
    for stage in ('03','04','05'):
        takes=stages.get(stage,{}).get('beats',[])
        index={}; order=[]
        for beat in takes:
            ident=beat.get('beat_id')
            if not ident: errors.append(f'{stage}: missing beat_id');continue
            if ident in index:errors.append(f'{stage}:{ident}: duplicate beat_id')
            index[ident]=beat;order.append(ident)
        indexes[stage]=(index,order)
    baseline,order=indexes['03']
    for ident,beat in baseline.items():
        for field in FIELDS:
            if field not in beat:errors.append(f'03:{ident}: missing {field}')
        if beat.get('dramatic_function') not in FUNCTIONS:errors.append(f'03:{ident}: invalid dramatic_function')
        if beat.get('tempo_intent') not in TEMPOS:errors.append(f'03:{ident}: invalid tempo_intent')
        if beat.get('dramatic_function')=='REVERSAL' and beat.get('reversal_trigger') in (None,'','NONE'):errors.append(f'03:{ident}: reversal lacks trigger')
        if beat.get('dramatic_function')=='PAYOFF' and beat.get('result_evidence') in (None,'','NONE'):errors.append(f'03:{ident}: payoff lacks evidence')
        if beat.get('source_event_ids') in (None,[], 'NONE'):errors.append(f'03:{ident}: missing source anchors')
    for stage in ('04','05'):
        index,sequence=indexes[stage]
        if sequence!=order:errors.append(f'{stage}: beat order drift')
        for ident,beat in baseline.items():
            if ident not in index:errors.append(f'{stage}:{ident}: missing beat');continue
            for field in FIELDS:
                if beat.get(field)!=index[ident].get(field):errors.append(f'{stage}:{ident}: drift {field}')
        for ident in index.keys()-baseline.keys():errors.append(f'{stage}:{ident}: extra beat')
    return errors
