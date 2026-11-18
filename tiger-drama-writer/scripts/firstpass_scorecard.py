#!/usr/bin/env python3
"""Read-only raw-vs-revised experiment scorecard. Never relabel rewrites as first-pass wins."""
import argparse, hashlib, json
from pathlib import Path
from audit_script_batch import audit
from release_gate import evaluate
from audit_script_batch import EP
import re

def split_episode_text(path):
    text=Path(path).read_text(encoding='utf-8')
    matches=list(EP.finditer(text))
    result={}
    for i,m in enumerate(matches):
        num=int(m.group(1))
        if num in result: raise ValueError(f'Duplicate episode heading: EP{num:02d}')
        result[num]=text[m.start():(matches[i+1].start() if i+1<len(matches) else len(text))].strip()
    return result

def episode_ready_map(path):
    # Diagnose each source episode independently, without masking global batch problems.
    from tempfile import TemporaryDirectory
    chunks=split_episode_text(path)
    out={}
    with TemporaryDirectory() as d:
        for n,body in chunks.items():
            f=Path(d)/f'EP{n:02d}.md'; f.write_text(body,encoding='utf-8')
            out[n]=evaluate([str(f)])['batch_screening_ready']
    return out

def score(raw, revised=None):
    raw=Path(raw).resolve()
    if not raw.is_file(): raise FileNotFoundError(raw)
    ra=audit(str(raw)); rg=evaluate([str(raw)])
    raw_eps={e['episode']:e for e in ra.get('episodes',[])}
    rows=[]
    raw_text=split_episode_text(raw); raw_ready=episode_ready_map(raw)
    rev_text={}
    rev_ready={}
    rev_eps={}
    revised_gate=None
    if revised:
        revised=Path(revised).resolve()
        if not revised.is_file(): raise FileNotFoundError(revised)
        rev_eps={e['episode']:e for e in audit(str(revised)).get('episodes',[])}
        rev_text=split_episode_text(revised); rev_ready=episode_ready_map(revised)
        if set(raw_text)!=set(rev_text): raise ValueError('Raw/revised episode sets differ; cannot compare like-for-like')
        revised_gate=evaluate([str(revised)])
    for n,ep in sorted(raw_eps.items()):
        revision=rev_eps.get(n)
        rows.append({'episode':n,'raw_structural_reviewable':ep.get('status')=='STRUCTURALLY_REVIEWABLE',
                     'revised_structural_reviewable':None if revision is None else revision.get('status')=='STRUCTURALLY_REVIEWABLE',
                     'raw_episode_screening_ready':raw_ready.get(n,False),
                     'revised_episode_screening_ready':None if revision is None else rev_ready.get(n,False),
                     'revision_observed':None if revision is None else raw_text.get(n)!=rev_text.get(n),
                     'revision_count':'UNKNOWN' if revision is not None else 0})
    return {'raw_file':str(raw),'raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
            'raw_episode_count':len(rows),'raw_structural_pass_count':sum(x['raw_structural_reviewable'] for x in rows),
            'raw_batch_screening_ready':rg['batch_screening_ready'],'raw_batch_issues':rg['files'][0]['issues'],
            'revised_file':None if not revised else str(revised),'revised_batch_screening_ready':None if revised_gate is None else revised_gate['batch_screening_ready'],
            'revised_batch_issues':None if revised_gate is None else revised_gate['files'][0]['issues'],
            'rows':rows,'measured_readthrough':False,'independent_voice_test':False,
            'note':'Structural counts are not quality or runtime claims. Revision count unknown without immutable per-pass logs. No invented metrics.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('--revised');p.add_argument('--output');a=p.parse_args()
    result=score(a.raw,a.revised);s=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(s,encoding='utf-8')
    print(s)
