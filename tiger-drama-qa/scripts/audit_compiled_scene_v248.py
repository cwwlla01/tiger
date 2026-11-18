import json, hashlib, sys
from pathlib import Path

def audit(root):
 root=Path(root); m=json.loads((root/'manifest.json').read_text(encoding='utf-8')); errors=[]
 shots=m.get('shots',[]); ids=[s.get('shot_id') for s in shots]; beats=[s.get('source_beat_id') for s in shots]
 if ids!=['S01','S02','S03','S04']: errors.append('SHOT_ORDER')
 if beats!=['B1','B2','B3','B4']: errors.append('BEAT_COVERAGE')
 if sum(s.get('duration_estimate_s',0) for s in shots)!=16: errors.append('DURATION')
 for name,digest in m.get('files',{}).items():
  p=root/name
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:errors.append('FILE_HASH:'+name)
 for n in ('04-画面帧生成提示词.md','05-视频生成提示词.md'):
  if n not in m.get('files',{}):errors.append('MISSING:'+n);continue
  if not (root/n).is_file():errors.append('MISSING_FILE:'+n);continue
  t=(root/n).read_text(encoding='utf-8')
  for shot,beat in zip(ids,beats):
   if f'{shot} / {beat} /' not in t:errors.append('PROMPT_MAPPING:'+n+':'+str(shot))
 s3=next((s for s in shots if s.get('shot_id')=='S03'),{})
 s4=next((s for s in shots if s.get('shot_id')=='S04'),{})
 if '不旋转门把' not in s3.get('action','') or '仍握住' not in s3.get('end_state',''):errors.append('S03_CONTINUITY')
 if '先' not in s4.get('audio','') or '后' not in s4.get('audio','') or '声音停止' not in s4.get('audio',''):errors.append('S04_SOUND_ORDER')
 if '尚未松开' not in s4.get('first_frame',''):errors.append('PREMATURE_RELEASE')
 for s in shots:
  if '门关闭' not in s.get('first_frame','') and '门关闭' not in s.get('end_state',''):errors.append('DOOR_STATE:'+s.get('shot_id',''))
 return {'status':'STRUCTURE_ONLY' if not errors else 'BLOCKED','errors':errors,'shot_count':len(shots)}

if __name__=='__main__':
 print(json.dumps(audit(sys.argv[1]),ensure_ascii=False,indent=2))
