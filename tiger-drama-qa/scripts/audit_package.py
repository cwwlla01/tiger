#!/usr/bin/env python3
"""Conservative package preflight. Never asserts semantic or visual acceptance."""
import argparse, hashlib, json
from pathlib import Path

def audit(root):
    root=Path(root)
    candidates={
        '02_tasks':'02-资产生成任务清单.json',
        '02_prompts':'02-资产生成提示词-EP001-EP002-候选版.md',
        '03_storyboard':'03-专业导演分镜.md',
        '04_frames':'04-画面帧生成提示词.md',
        '05_video':'05-视频生成提示词.md',
    }
    files={}; flags=[]
    for key,name in candidates.items():
        p=root/name
        if p.is_file():
            files[key]={'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
        else:
            files[key]={'status':'MISSING'}
            flags.append({'severity':'NOT_VERIFIED','code':'INPUT_MISSING','file':name})
    tasks_info={'status':'NOT_VERIFIED'}
    p=root/candidates['02_tasks']
    if p.is_file():
        try:
            data=json.loads(p.read_text(encoding='utf-8'))
            tasks=data['tasks'] if isinstance(data,dict) else data
            if not isinstance(tasks,list): raise ValueError('tasks must be list')
            tasks_info={'count':len(tasks),'status':'STRUCTURE_CHECKED'}
            for i,t in enumerate(tasks):
                if not isinstance(t,dict):
                    flags.append({'severity':'P0','code':'INVALID_TASK','index':i});continue
                if t.get('image_status')=='IMAGE_MISSING' or t.get('status')=='IMAGE_MISSING' or any(v=='IMAGE_MISSING' for v in t.values()):
                    flags.append({'severity':'NOT_VERIFIED','code':'IMAGE_MISSING','index':i})
                if not any(isinstance(t.get(k),str) and t[k].strip() for k in ('prompt','image_prompt','generation_prompt','prompt_text')):
                    flags.append({'severity':'P1','code':'PROMPT_FIELD_UNDETECTED','index':i})
        except (ValueError,KeyError,UnicodeError) as exc:
            flags.append({'severity':'P0','code':'TASK_JSON_INVALID','detail':str(exc)})
    return {'kind':'STRUCTURAL_PREFLIGHT_ONLY','files':files,'tasks':tasks_info,'flags':flags,
            'gate_decisions':{f'G{i}':'NOT_VERIFIED' for i in range(1,7)},
            'production_acceptance':'NOT_VERIFIED'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',required=True);a.add_argument('--output');ns=a.parse_args()
    result=audit(ns.root);s=json.dumps(result,ensure_ascii=False,indent=2)
    if ns.output:Path(ns.output).write_text(s+'\n',encoding='utf-8')
    else:print(s)
