"""V2.13 structural suspense handoff audit; not a cinematic quality judge."""
import json,sys
from pathlib import Path
VALID={'SHOW','WITHHOLD','REACTION_ONLY','AUDIO_ONLY','POST_ONLY'}
def audit(data):
 errors=[]; beats=data.get('source_beats',[]); ids=[b.get('id') for b in beats]
 if not ids or len(ids)!=len(set(ids)) or any(not b.get('anchor') for b in beats): errors.append('SOURCE_BEATS_INVALID')
 required=set(ids); edges=[(b['id'],next_id) for b in beats for next_id in b.get('must_precede',[]) if b.get('id')]
 for a,b in edges:
  if b not in required: errors.append('UNKNOWN_ORDER_TARGET:'+b)
 stages=data.get('stages',{}); director=stages.get('03',[])
 if not director: errors.append('DIRECTOR_MISSING')
 dmap={}; sequence=[]
 for take in director:
  tid=take.get('take_id'); bs=take.get('beat_ids',[])
  if not tid or tid in dmap: errors.append('DUPLICATE_TAKE:'+str(tid))
  dmap[tid]=take
  if take.get('reveal_policy') not in VALID: errors.append('POLICY_INVALID:'+str(tid))
  for b in bs:
   if b not in required: errors.append('UNKNOWN_BEAT:'+str(b))
   sequence.append(b)
 for b in required-set(sequence): errors.append('BEAT_MISSING:'+str(b))
 first={b:sequence.index(b) for b in required if b in sequence}
 for a,b in edges:
  if a in first and b in first and first[a]>=first[b]: errors.append('ORDER_BROKEN:'+a+':'+b)
 for stage in ('04','05'):
  if stage not in stages: continue
  actual=stages[stage]; amap={t.get('take_id'):t for t in actual}
  if len(amap)!=len(actual): errors.append('DUPLICATE_DOWNSTREAM:'+stage)
  for tid,d in dmap.items():
   if tid not in amap: errors.append('TAKE_MISSING:'+stage+':'+str(tid)); continue
   t=amap[tid]
   for field in ('beat_ids','reveal_policy'):
    if t.get(field)!=d.get(field): errors.append('DRIFT:'+stage+':'+str(tid)+':'+field)
  for tid in amap.keys()-dmap.keys(): errors.append('EXTRA_TAKE:'+stage+':'+str(tid))
 return sorted(set(errors))
if __name__=='__main__':
 data=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
 errors=audit(data);print(json.dumps({'ok':not errors,'errors':errors},ensure_ascii=False,indent=2));sys.exit(bool(errors))
