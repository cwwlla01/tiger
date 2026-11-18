#!/usr/bin/env python3
"""Static take audit, not actual video validation."""
import json,sys
from pathlib import Path

def audit(d):
 e=[];w=[]; shots={s.get('director_shot_id') for s in d.get('shots',[])}
 takes=d.get('takes',[])
 if d.get('approval_status')!='APPROVED' and takes:e.append('Takes require approved director route')
 if len({t.get('take_id') for t in takes})!=len(takes):e.append('Duplicate take IDs')
 for t in takes:
  name=t.get('take_id','?'); gen=t.get('generation_duration_s'); edit=t.get('edit_duration_s')
  if not isinstance(gen,(int,float)) or gen<=0:e.append(f'{name}: invalid generation seconds')
  if not isinstance(edit,(int,float)) or edit<=0:e.append(f'{name}: invalid edit seconds')
  if isinstance(gen,(int,float)) and isinstance(edit,(int,float)) and edit>gen:e.append(f'{name}: edit exceeds generation')
  if isinstance(gen,(int,float)) and gen<4:w.append(f'{name}: below user workflow 4s minimum; verify interface')
  if not set(t.get('shot_ids',[])).issubset(shots):e.append(f'{name}: unknown shot IDs')
  if not t.get('prompt'):w.append(f'{name}: missing prompt')
  for ref in t.get('references',[]):
   if ref.get('status')=='EXISTS' and not ref.get('asset_id'):e.append(f'{name}: EXISTS reference without asset_id')
  if len(t.get('shot_ids',[]))>1 and not t.get('multishot_pilot_passed'):w.append(f'{name}: multishot not pilot-validated')
 return e,w
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));e,w=audit(d)
 print(json.dumps({'passed':not e,'errors':e,'warnings':w},ensure_ascii=False,indent=2));sys.exit(bool(e))
