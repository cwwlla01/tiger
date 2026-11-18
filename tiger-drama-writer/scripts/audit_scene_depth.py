#!/usr/bin/env python3
"""Flag scenes that resemble short beat summaries; not a semantic quality certificate."""
import argparse,json,re
from pathlib import Path
from audit_script_batch import EP,SC,SPEECH,han

def audit(path, *, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH, source_text=None):
    s=source_text if source_text is not None else Path(path).read_text(encoding='utf-8'); eps=list(episode_pattern.finditer(s)); out=[]
    for i,e in enumerate(eps):
        body=s[e.end():eps[i+1].start() if i+1<len(eps) else len(s)]
        cuts=list(scene_pattern.finditer(body)); scenes=[]
        for k,c in enumerate(cuts):
            chunk=body[c.end():cuts[k+1].start() if k+1<len(cuts) else len(body)]
            dialogue=speech_pattern.findall(chunk)
            count=han(chunk); actions=han(speech_pattern.sub('',chunk))
            flags=[]
            if count<230:flags.append('SCENE_UNDERDEVELOPED_REVIEW')
            if len(dialogue)<5:flags.append('SCENE_DIALOGUE_TOO_SPARSE_REVIEW')
            if actions<65:flags.append('SCENE_ACTION_TOO_THIN_REVIEW')
            scenes.append({'scene':c.group(0).strip(),'body_han':count,'dialogue_turns':len(dialogue),'action_han':actions,'flags':flags})
        weak=sum(bool(x['flags']) for x in scenes)
        out.append({'episode':int(e.group(1)),'scenes':scenes,'weak_scenes':weak,'risk':'SCENE_DEPTH_REVIEW' if weak else 'NO_SCENE_DEPTH_FLAGS'})
    return {'file':str(path),'episodes':out,'note':'Thresholds are diagnostic heuristics; static checks cannot certify dramatic causality or runtime.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('files',nargs='+');p.add_argument('--output');a=p.parse_args()
    result={'files':[audit(x) for x in a.files]}; content=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(content,encoding='utf-8')
    print(content)
