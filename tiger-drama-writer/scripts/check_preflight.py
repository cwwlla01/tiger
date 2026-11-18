#!/usr/bin/env python3
"""Validate a five-episode pre-draft causal contract. Structural only; not art quality."""
import argparse, json
from pathlib import Path
REQUIRED = ('objective','obstacle','choice','price','state_change','payoff','end_turn','scenes')
SCENE_FIELDS = ('location','action','reversal')

def audit(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    episodes=data.get('episodes',[]); results=[]; ids=[]
    for ep in episodes:
        ident=ep.get('episode'); ids.append(ident)
        errors=[]
        for f in REQUIRED:
            v=ep.get(f)
            if not v or (isinstance(v,str) and len(v.strip())<8): errors.append('MISSING_OR_THIN_'+f.upper())
        scenes=ep.get('scenes',[])
        if not isinstance(scenes,list) or len(scenes)<3: errors.append('FEWER_THAN_THREE_PLANNED_SCENES')
        else:
            for n,sc in enumerate(scenes,1):
                for f in SCENE_FIELDS:
                    if not isinstance(sc,dict) or len(str(sc.get(f,'' )).strip())<6:
                        errors.append(f'SCENE_{n}_{f.upper()}_MISSING')
        results.append({'episode':ident,'passed':not errors,'flags':errors})
    if len(episodes)!=5: global_flags=['EXPECTED_FIVE_EPISODES']
    else: global_flags=[]
    if len(set(ids))!=len(ids): global_flags.append('DUPLICATE_EPISODE_IDS')
    if all(isinstance(i,int) for i in ids) and ids!=list(range(ids[0],ids[0]+len(ids))): global_flags.append('NONCONSECUTIVE_EPISODES')
    return {'file':str(path),'preflight_passed':not global_flags and all(r['passed'] for r in results),'global_flags':global_flags,'episodes':results,'note':'Preflight is a causal coverage prompt, not a screenplay quality or runtime certificate.'}
if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('file');a.add_argument('--output');args=a.parse_args();result=audit(args.file);out=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(out,encoding='utf-8')
    print(out)
