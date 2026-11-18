#!/usr/bin/env python3
"""Inspect author-reviewed episode-mechanism ledger; evidence binding is not semantic approval."""
import argparse, json, re, hashlib
from pathlib import Path

def inspect(script_text, ledger):
    chunks = re.split(r'(?=^##\s*EP\d{1,3}\b)', script_text, flags=re.M)
    episodes={}
    for chunk in chunks:
        m=re.match(r'^##\s*(EP\d{1,3})\b',chunk)
        if m: episodes[m.group(1)]=chunk
    errors=[]; labels=[]
    for item in ledger['episodes']:
        eid=item['episode']; chunk=episodes.get(eid,'')
        if not chunk: errors.append(eid+': missing episode'); continue
        for key in ('mechanism','decisive_action','cost','state_change'):
            if not item.get(key): errors.append(eid+': missing '+key)
        for key in ('decisive_action','cost','state_change'):
            quote=item.get(key,'')
            if quote and quote not in chunk: errors.append(eid+': ungrounded '+key)
        labels.append((eid,item.get('mechanism','')))
    for i in range(2,len(labels)):
        if len({x[1] for x in labels[i-2:i+1]})==1:
            errors.append('three consecutive episodes repeat mechanism '+labels[i][1])
    if len({x['episode'] for x in ledger['episodes']})!=len(ledger['episodes']):
        errors.append('duplicate episode')
    return {'ok':not errors,'errors':errors,'episodes_checked':len(ledger['episodes']),'script_sha256':hashlib.sha256(script_text.encode()).hexdigest()}

def main():
    p=argparse.ArgumentParser();p.add_argument('--script',required=True);p.add_argument('--ledger',required=True);p.add_argument('--output');a=p.parse_args()
    r=inspect(Path(a.script).read_text(),json.loads(Path(a.ledger).read_text()))
    if a.output:Path(a.output).write_text(json.dumps(r,ensure_ascii=False,indent=2))
    print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['ok'] else 2)
if __name__=='__main__':main()
