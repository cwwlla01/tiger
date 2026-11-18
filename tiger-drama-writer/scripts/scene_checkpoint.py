#!/usr/bin/env python3
"""Per-scene stop/go diagnostics for sequential screenplay drafting, never a semantic certificate."""
import argparse,json
from pathlib import Path
from audit_scene_depth import audit

def checkpoint(path, episode=None, scene=None):
    data=audit(path)['episodes']
    if episode is not None:data=[e for e in data if e['episode']==episode]
    if not data:raise ValueError('Episode not found')
    records=[]
    for e in data:
        for idx,s in enumerate(e['scenes'],1):
            if scene is not None and idx!=scene:continue
            warnings=list(s['flags'])
            if s['dialogue_turns']>=5 and s['action_han']<85:
                warnings.append('DIALOGUE_DOMINATES_ACTION_REVIEW')
            records.append({'episode':e['episode'],'scene_index':idx,'heading':s['scene'],'body_han':s['body_han'],'action_han':s['action_han'],'dialogue_turns':s['dialogue_turns'],'warnings':warnings,'checkpoint':'NEEDS_REALIZATION' if warnings else 'STATIC_READY_FOR_EDITORIAL_CHECK'})
    if not records:raise ValueError('Scene not found')
    return {'file':str(path),'scenes':records,'all_static_ready':all(not x['warnings'] for x in records),'caution':'No automatic test can certify dramatic turns, distinct character voice, emotional impact or runtime. Human scene reading remains required.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('--episode',type=int);p.add_argument('--scene',type=int);p.add_argument('--output');a=p.parse_args()
    result=checkpoint(a.script,a.episode,a.scene)
    output=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(output,encoding='utf8')
    print(output)
