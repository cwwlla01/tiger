#!/usr/bin/env python3
"""Strict sequential episode pipeline. Review and static authorization are separate.
Manifest: {episodes:[{number:1,file:'...',review:'...'}, ...]}.
Only an explicit authorized prior episode permits a subsequent one. All paths relative to manifest.
"""
import argparse, json
from pathlib import Path
from editorial_authorize import authorize
from episode_stop_gate import check

def run(manifest_path):
    manifest_path=Path(manifest_path).resolve()
    data=json.loads(manifest_path.read_text(encoding='utf-8'))
    entries=data.get('episodes',[])
    history=[]; expected=1; stopped=False; status='INCOMPLETE'
    if not isinstance(entries,list) or not entries:
        return {'status':'INVALID_MANIFEST','completed':0,'history':[],'issue':'EMPTY_EPISODE_LIST'}
    for entry in entries:
        if not isinstance(entry,dict) or type(entry.get('number')) is not int or entry['number']!=expected:
            status='BLOCKED_ORDER';history.append({'expected_episode':expected,'issue':'NON_SEQUENTIAL_EPISODE'});break
        f=(manifest_path.parent/entry.get('file','')).resolve()
        if not f.is_file():
            status='BLOCKED_MISSING_FILE';history.append({'episode':expected,'issue':'EPISODE_FILE_NOT_FOUND'});break
        static=check(f,expected)
        record={'episode':expected,'sha256':static['sha256'],'static_issues':static['issues'],'static_ready':static['static_ready_for_editorial_review']}
        if not static['static_ready_for_editorial_review']:
            record['issue']='STATIC_GATE_FAILED';history.append(record);status='BLOCKED_STATIC';break
        review=entry.get('review')
        if not review:
            record['issue']='EDITORIAL_REVIEW_MISSING';history.append(record);status='BLOCKED_EDITORIAL';break
        review_path=(manifest_path.parent/review).resolve()
        if not review_path.is_file():
            record['issue']='EDITORIAL_RECORD_NOT_FOUND';history.append(record);status='BLOCKED_EDITORIAL';break
        try: decision=authorize(f,expected,review_path)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as ex:
            record['issue']='EDITORIAL_RECORD_INVALID';history.append(record);status='BLOCKED_EDITORIAL';break
        record['editorial_issues']=decision['issues']
        record['authorized']=decision['next_episode_authorized']
        history.append(record)
        if not record['authorized']:
            status='BLOCKED_EDITORIAL';break
        expected+=1
    else:
        status='READY_FOR_SEPARATE_TIMED_AND_ARTISTIC_REVIEW'
    return {'status':status,'completed':sum(bool(h.get('authorized')) for h in history),'requested':len(entries),'history':history,'not_a_production_certificate':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--output');a=p.parse_args()
    result=run(a.manifest);s=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(s,encoding='utf-8')
    print(s)
    raise SystemExit(0 if result['status']=='READY_FOR_SEPARATE_TIMED_AND_ARTISTIC_REVIEW' else 2)
