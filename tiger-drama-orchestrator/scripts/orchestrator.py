#!/usr/bin/env python3
"""Read-only evidence scan and conservative orchestration plan. No Skill execution."""
import argparse, datetime, hashlib, json
from pathlib import Path

STAGES = {
 '01': ('tiger-drama-writer', ['剧本.md', '01-剧本.md']),
 '02': ('tiger-drama-assets', ['02-资产解析.md','02-资产生成提示词-EP001-EP002-候选版.md','02-资产总库.md']),
 '03': ('tiger-drama-director', ['03-专业导演分镜.md']),
 '04': ('tiger-video-prompt', ['04-画面帧生成提示词.md']),
 '05': ('tiger-video-prompt', ['05-视频生成提示词.md']),
 '06': ('tiger-drama-qa', ['06-全流程质量审核报告.md'])
}

def scan(project):
    root=Path(project).resolve()
    if not root.is_dir(): raise ValueError('Project directory not found')
    stages={}
    for key,(owner,names) in STAGES.items():
        artifacts=[]
        for name in names:
            p=root/name
            if p.is_file():
                artifacts.append({'path':name,'exists':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        stages[key]={'owner_skill':owner,'status':'NOT_VERIFIED' if artifacts else 'NOT_STARTED','artifacts':artifacts,'upstream_hashes':{}}
    return {'schema_version':1,'project':str(root),'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stages':stages,'authority':{},'blockers':[],'tickets':[],'history':[]}

def plan(state):
    stages=state['stages']; tasks=[]
    for key in STAGES:
        st=stages[key]
        if st['status']=='APPROVED':continue
        dependencies={'01':[],'02':['01'],'03':['01','02'],'04':['02','03'],'05':['02','03','04'],'06':['01','02','03','04','05']}[key]
        candidate_ready=[]
        authority_ready=[]
        review_required=[]
        for dep in dependencies:
            upstream=stages[dep]
            status=upstream['status']
            has_artifact=any(item.get('exists') for item in upstream.get('artifacts',[]))
            if status not in ('CANDIDATE','APPROVED') and not (status=='NOT_VERIFIED' and has_artifact):
                candidate_ready.append(dep)
            if status!='APPROVED':
                authority_ready.append(dep)
            if status=='NOT_VERIFIED' and has_artifact:
                review_required.append(dep)
        tasks.append({
            'stage':key,
            'owner_skill':st['owner_skill'],
            'status':st['status'],
            'action':'VERIFY_AUTHORITY_OR_REPAIR' if st['artifacts'] else 'PRODUCE_CANDIDATE',
            'unresolved_upstream':candidate_ready,
            'upstream_review_required':review_required,
            'unapproved_upstream':authority_ready,
            'ready_for_candidate':not candidate_ready,
            'ready_for_authoritative_handoff':not authority_ready
        })
    return {'project':state['project'],'note':'Plan only. No professional Skill invoked and no approval inferred.','tasks':tasks}

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['scan','plan']);p.add_argument('--project');p.add_argument('--state');p.add_argument('--write-state',action='store_true');a=p.parse_args()
    if a.command=='scan':
        if not a.project: p.error('--project required for scan')
        result=scan(a.project)
        if a.write_state:
            if not a.state:p.error('--state required with --write-state')
            dest=Path(a.state)
            if dest.exists():p.error('Refusing to overwrite existing state; preserve approvals/history')
            dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        if not a.state:p.error('--state required for plan')
        result=plan(json.loads(Path(a.state).read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
