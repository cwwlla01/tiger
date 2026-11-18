#!/usr/bin/env python3
"""Static source/route/shot audit. Usage: python audit_storyboard.py plan.json"""
import json,sys
from pathlib import Path

def audit(d):
 errors=[]; warnings=[]
 events={e.get('id') for e in d.get('source_events',[]) if isinstance(e,dict)}
 if not events: errors.append('Missing source_events')
 routes=d.get('routes',[]); ids=[r.get('id') for r in routes]
 if len(routes)<2 or len(set(ids))!=len(ids):errors.append('Need two distinct director routes')
 for r in routes:
  if len(r.get('information_schedule',[]))!=5:warnings.append(f"Route {r.get('id')} needs five viewer information states")
  if not r.get('editorial_mechanism'):warnings.append(f"Route {r.get('id')} lacks editorial mechanism")
 if d.get('recommended_route') not in ids:errors.append('recommended_route must match route id')
 if not d.get('visual_bible'):errors.append('Missing visual_bible')
 if d.get('approval_status') not in ('PENDING','APPROVED','REJECTED'):errors.append('Invalid approval_status')
 shots=d.get('shots',[])
 if len({s.get('director_shot_id') for s in shots})!=len(shots):errors.append('Duplicate shot IDs')
 for s in shots:
  sid=s.get('director_shot_id','?')
  if not set(s.get('source_event_ids',[])).issubset(events):errors.append(f'{sid}: unknown source event')
  for k in ('audience_focus','dramatic_function','entry_state','exit_state'):
   if not s.get(k):warnings.append(f'{sid}: missing {k}')
 if d.get('approval_status')=='PENDING' and d.get('takes'):errors.append('Pending director approval: no final takes')
 if d.get('qa',{}).get('media')=='PASSED' and not d.get('qa',{}).get('media_evidence'):errors.append('Media QA passed without evidence')
 return errors,warnings
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));e,w=audit(d)
 print(json.dumps({'passed':not e,'errors':e,'warnings':w},ensure_ascii=False,indent=2));sys.exit(bool(e))
