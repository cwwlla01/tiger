from pathlib import Path
import hashlib,json,re

def audit(folder):
    folder=Path(folder)
    src=folder/'01-原始测试剧本.md'; out=folder/'03-专业导演分镜.md'; m=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    text=out.read_text(encoding='utf-8'); source=src.read_text(encoding='utf-8')
    errors=[]
    for p,key in [(src,'source_sha256'),(out,'storyboard_sha256')]:
        if hashlib.sha256(p.read_bytes()).hexdigest()!=m[key]:errors.append(key+'_MISMATCH')
    ids=re.findall(r'^### (S\d\d)｜',text,re.M)
    if ids!=m['shot_ids'] or len(ids)!=9:errors.append('SHOT_COVERAGE')
    if m['source_beats']!=list(range(1,10)):errors.append('BEAT_COVERAGE')
    if m['independent_blind_run'] or m['real_video_test']:errors.append('UNSUPPORTED_CLAIM')
    for s in ['第三声','切黑','左手','右手','未回头','不触碰','暖光']:
        if s not in text:errors.append('MISSING_'+s)
    if '第三声敲击' not in source:errors.append('INVALID_SOURCE')
    return {'status':'TEST_SCRIPT_STRUCTURE_ONLY' if not errors else 'BLOCKED','errors':errors,'shots':len(ids)}

if __name__=='__main__':
 import sys
 print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
