#!/usr/bin/env python3
"""Stop-on-failure checkpoint for a single immutable first-pass episode.
Exit 2 if static issues exist. Never equate success with editorial quality.
"""
import argparse, hashlib, json, re
from pathlib import Path
from release_gate import evaluate
from audit_script_batch import EP

def check(path, expected):
    p=Path(path); raw=p.read_bytes(); content=raw.decode('utf-8'); found=[int(x.group(1)) for x in EP.finditer(content)]
    issues=[]
    if found != [expected]: issues.append('WRONG_OR_MULTIPLE_EPISODE_HEADINGS')
    gate=evaluate([str(p)])
    issues += gate['files'][0]['issues']
    return {'episode':expected,'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),
            'static_ready_for_editorial_review':not issues,'issues':sorted(set(issues)),
            'next_episode_allowed_by_static_gate':not issues,
            'editorial_review_required':True,
            'next_episode_authorized':False,
            'warning':'Passing is static only; editorial and timed-read gates remain open.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('file');ap.add_argument('--episode',type=int,required=True);ap.add_argument('--output')
    args=ap.parse_args(); result=check(args.file,args.episode); data=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(data,encoding='utf-8')
    print(data)
    raise SystemExit(0 if result['next_episode_allowed_by_static_gate'] else 2)
