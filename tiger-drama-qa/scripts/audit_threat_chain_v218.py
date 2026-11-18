"""Conservative structural check for Tiger V2.18. JSON input: stages.03/04/05.takes[]."""
import json, sys
FIELDS = ('beat_ids','source_event_ids','threat_id','threat_state_before','threat_state_after','action_owner','cause','effect','cost_or_consequence','knowledge_reveal','screen_direction','prop_custody','camera_intent')

def audit(data):
    issues=[]
    stages=data.get('stages',{})
    indexes={}
    for stage in ('03','04','05'):
        seen={}
        for t in stages.get(stage,{}).get('takes',[]):
            ident=t.get('take_id')
            if not ident:
                issues.append(f'{stage}: missing take_id');continue
            if ident in seen:issues.append(f'{stage}:{ident}: duplicate take_id')
            seen[ident]=t
        indexes[stage]=seen
    base=indexes['03']
    for ident,t in base.items():
        for f in FIELDS:
            if f not in t:issues.append(f'03:{ident}: missing {f}')
    for stage in ('04','05'):
        for ident,t in base.items():
            if ident not in indexes[stage]:issues.append(f'{stage}:{ident}: missing take');continue
            for f in FIELDS:
                if t.get(f)!=indexes[stage][ident].get(f):issues.append(f'{stage}:{ident}: drift {f}')
        for ident in indexes[stage].keys()-base.keys():issues.append(f'{stage}:{ident}: extra take')
    return issues

if __name__=='__main__':
    with open(sys.argv[1],encoding='utf-8') as f: data=json.load(f)
    issues=audit(data)
    print(json.dumps({'passed':not issues,'issues':issues},ensure_ascii=False,indent=2))
    sys.exit(bool(issues))
