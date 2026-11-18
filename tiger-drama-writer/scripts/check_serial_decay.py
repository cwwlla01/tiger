#!/usr/bin/env python3
"""Warn on late-episode compression; not a literary-quality verdict."""
import argparse,json,sys
from audit_script_batch import audit

def assess(path):
    d=audit(path); rows=d.get('episodes',[])
    if not rows:return {'file':str(path),'issues':['NO_EPISODES']}
    baseline=rows[0]['body_han']
    issues=[]
    for i,r in enumerate(rows):
        if i and r['body_han']<900:issues.append(f"EP{r['episode']:02d}_THIN")
        if i and baseline>=900 and r['body_han'] < .8*baseline:issues.append(f"EP{r['episode']:02d}_SHRINKS_OVER_20_PERCENT")
    if len(rows)>=5 and sum(r['body_han']<900 for r in rows[-4:])>=3:issues.append('LATE_BATCH_COMPRESSION')
    return {'file':str(path),'episodes':[{'episode':r['episode'],'body_han':r['body_han']} for r in rows],'issues':issues,'note':'Flagged length is a review signal, not a pass/fail verdict on artistic quality.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('files',nargs='+');p.add_argument('--output');a=p.parse_args()
    result={'results':[assess(f) for f in a.files]}; rendered=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:open(a.output,'w',encoding='utf8').write(rendered)
    print(rendered)
