"""V2.17 structural cross-stage action beat audit; no media quality claims."""
import json
import sys
from pathlib import Path

FIELDS = ('actor_ids', 'target_ids', 'prop_custody_before', 'prop_custody_after', 'screen_direction', 'contact_event', 'observable_end_state', 'knowledge_after')

def audit(bundle):
    issues=[]
    stages=bundle.get('stages', {})
    maps={}
    for stage in ('03','04','05'):
        beats=stages.get(stage, {}).get('beats', [])
        found={}
        for beat in beats:
            bid=beat.get('beat_id')
            if not bid:
                issues.append(f'{stage}: MISSING_BEAT_ID')
            elif bid in found:
                issues.append(f'{stage}:{bid}: DUPLICATE_BEAT')
            else:
                found[bid]=beat
        maps[stage]=found
    for bid,src in maps['03'].items():
        for key in ('source_anchor','action','take_ids',*FIELDS):
            if key not in src:
                issues.append(f'03:{bid}: MISSING_{key.upper()}')
        for stage in ('04','05'):
            dst=maps[stage].get(bid)
            if dst is None:
                issues.append(f'{stage}:{bid}: MISSING_BEAT')
                continue
            for key in FIELDS:
                if key not in dst or dst[key]!=src.get(key):
                    issues.append(f'{stage}:{bid}: DRIFT_{key.upper()}')
    for stage in ('04','05'):
        for bid in maps[stage].keys()-maps['03'].keys():
            issues.append(f'{stage}:{bid}: UNSOURCED_BEAT')
    return {'passed':not issues,'issues':sorted(issues),'beat_count':len(maps['03'])}

if __name__=='__main__':
    result=audit(json.loads(Path(sys.argv[1]).read_text()))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['passed'] else 1)
