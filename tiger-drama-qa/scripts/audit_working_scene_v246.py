import hashlib,json
from pathlib import Path

def audit(root):
 root=Path(root)
 try:
  m=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
  source=json.loads((root/'source.json').read_text(encoding='utf-8'))
  draft=(root/'03-working-draft.md').read_bytes()
 except (OSError,ValueError) as exc:return {'status':'INVALID','reason':str(exc)}
 if m.get('historical_independent_runs') is not False or m.get('evidence_type')!='WORKING_DRAFT':return {'status':'INVALID','reason':'unsupported provenance claim'}
 if hashlib.sha256((root/'source.json').read_bytes()).hexdigest()!=m.get('source_sha256') or hashlib.sha256(draft).hexdigest()!=m.get('draft_sha256'):return {'status':'INVALID','reason':'hash mismatch'}
 ids=[b['id'] for b in source['beats']]
 shots=m['shots']; got=[b for s in shots for b in s['beat_ids']]
 if len(set(s['shot_id'] for s in shots))!=len(shots):return {'status':'INVALID','reason':'duplicate shot id'}
 if set(got)!=set(ids) or len(got)!=len(ids):return {'status':'INVALID','reason':'beat coverage mismatch'}
 if any(s['duration_s']<=0 for s in shots):return {'status':'INVALID','reason':'duration invalid'}
 return {'status':'EXPLORATORY_ONLY','shots':len(shots),'duration_s':sum(s['duration_s'] for s in shots),'beats':len(ids)}

if __name__=='__main__':
 import sys
 print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
