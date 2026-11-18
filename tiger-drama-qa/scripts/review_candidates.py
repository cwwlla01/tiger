#!/usr/bin/env python3
"""Independently verify candidate integrity and required evidence; never self-approve semantics."""
import argparse, hashlib, json
from pathlib import Path

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def review(root, repair_report, output):
    root=Path(root).resolve(); repair_report=Path(repair_report).resolve(); output=Path(output).resolve()
    data=json.loads(repair_report.read_text(encoding='utf-8'))
    rows=[]
    for t in data.get('tickets',[]):
        row={'ticket_id':t.get('ticket_id'),'status':'BLOCKED','checks':{}}
        if t.get('status')!='CANDIDATE_WRITTEN_NEEDS_INDEPENDENT_REVIEW':
            row['reason']='no candidate to review';rows.append(row);continue
        name=t.get('file',''); source=(root/name).resolve(); candidate=(repair_report.parent/'candidates'/name).resolve()
        safe=bool(name.startswith(('02-','04-','05-')) and name.endswith('.md') and source.parent==root and candidate.parent==repair_report.parent/'candidates')
        row['checks']['allowed_path']=safe
        if not safe or not source.is_file() or not candidate.is_file():
            row['reason']='missing or unsafe source/candidate';rows.append(row);continue
        row['checks']['source_unchanged']=sha(source)==t.get('before_sha256')
        row['checks']['candidate_hash_matches']=sha(candidate)==t.get('after_sha256')
        row['checks']['evidence_recorded']=bool(t.get('source_evidence') and t.get('rationale') and t.get('owner'))
        row['checks']['diff_recorded']=bool(t.get('diff'))
        row['status']='READY_FOR_INDEPENDENT_SEMANTIC_REVIEW' if all(row['checks'].values()) else 'BLOCKED'
        if row['status']=='BLOCKED':row['reason']='integrity or provenance check failed'
        rows.append(row)
    result={'kind':'INDEPENDENT_CANDIDATE_REVIEW','acceptance':'NOT_VERIFIED','tickets':rows,'closed_tickets':0,'note':'Integrity checks do not validate story semantics. Independent source-grounded reviewer and production owner must sign off separately.'}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--repair-report',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    print(json.dumps(review(a.root,a.repair_report,a.output),ensure_ascii=False))
