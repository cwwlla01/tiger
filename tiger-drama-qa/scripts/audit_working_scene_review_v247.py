import hashlib,json
from pathlib import Path

def audit(root):
 root=Path(root)
 try:
  manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
  src=(root/'source.json').read_bytes(); raw=(root/'03-revised-draft.md').read_bytes()
  source=json.loads(src)
 except (OSError,ValueError) as e:return {'status':'INVALID','reason':str(e)}
 if manifest.get('evidence_type')!='WORKING_DRAFT_REVIEW' or manifest.get('historical_independent_runs') is not False:return {'status':'INVALID','reason':'provenance'}
 if hashlib.sha256(src).hexdigest()!=manifest.get('source_sha256') or hashlib.sha256(raw).hexdigest()!=manifest.get('draft_sha256'):return {'status':'INVALID','reason':'hash mismatch'}
 shots=manifest.get('shots',[]); beats=[b['id'] for b in source['beats']]
 ids=[s.get('shot_id') for s in shots]; covered=[b for s in shots for b in s.get('beat_ids',[])]
 if len(ids)!=len(set(ids)) or sorted(covered)!=sorted(beats):return {'status':'INVALID','reason':'coverage or duplicate shot'}
 if any(not isinstance(s.get('duration_s'),(int,float)) or s['duration_s']<=0 for s in shots):return {'status':'INVALID','reason':'duration'}
 if any(s.get('axis')!='same' for s in shots):return {'status':'INVALID','reason':'axis'}
 if not any(s.get('action')=='hold' for s in shots) or not any(s.get('action')=='release_after_stop' for s in shots):return {'status':'INVALID','reason':'action causal chain'}
 required={'S02_CUT_AMBIGUITY','S03_UNNECESSARY_MOVE','S04_AUDIO_ACTION_ORDER','S03_S04_HAND_CONTINUITY'}
 if not required.issubset(set(manifest.get('review_findings',[]))):return {'status':'INVALID','reason':'review trace'}
 text=raw.decode('utf-8')
 for phrase in ['同轴切至中景','固定中近景','声音停止后','同一只手','不展示门内实体']:
  if phrase not in text:return {'status':'INVALID','reason':'missing editorial evidence: '+phrase}
 return {'status':'WORKING_DRAFT_REVIEWED','shots':len(shots),'beats':len(beats),'duration_s':sum(s['duration_s'] for s in shots),'historical_ab':False}

if __name__=='__main__':
 import sys
 print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
