#!/usr/bin/env python3
"""Role-based QA triage and safe copy-on-write repairs; never edit authoritative sources."""
import argparse, difflib, hashlib, json, re
from pathlib import Path

ROLES = {
 'source': ('来源与版本审计员','G1'), 'asset': ('资产身份与阶段审计员','G2'),
 'image': ('图像与版本审计员','G3'), 'director': ('导演剧情与空间审计员','G4'),
 'continuity': ('跨镜头连续性审计员','G4'), 'binding': ('参考图绑定审计员','G5'),
 'video': ('成片与动作审计员','G6'), 'arbiter': ('独立终审员','ALL')
}
RULES = {
 'INPUT_MISSING': ('source','MANUAL'), 'TASK_JSON_INVALID': ('asset','MANUAL'),
 'INVALID_TASK': ('asset','MANUAL'), 'IMAGE_MISSING': ('image','MANUAL'),
 'PROMPT_FIELD_UNDETECTED': ('asset','MANUAL'),
 'TRAILING_WHITESPACE': ('source','SAFE_AUTO'), 'EXCESS_BLANK_LINES': ('source','SAFE_AUTO')
}
def digest(b): return hashlib.sha256(b).hexdigest()
def fix_format(text):
    lines=[re.sub(r'[ \t]+$', '', line) for line in text.split('\n')]
    cleaned='\n'.join(lines)
    cleaned=re.sub(r'\n{4,}', '\n\n\n', cleaned)
    return cleaned

def run(root, output, apply=False):
    root=Path(root).resolve(); output=Path(output).resolve()
    if output==root or root in output.parents and output.name=='.':
        raise ValueError('output cannot equal source root')
    output.mkdir(parents=True, exist_ok=True)
    from audit_package import audit
    pre=audit(root)
    findings=[]; changes=[]
    for f in pre['flags']:
        role,mode=RULES.get(f['code'],('arbiter','MANUAL'))
        findings.append({**f,'role':role,'gate':ROLES[role][1],'fix_mode':mode,'state':'OPEN'})
    # Scope is deliberately restricted to 02/04/05 markdown; no edits to 01/03 authoritative sources.
    for pattern in ('02-*.md','04-*.md','05-*.md'):
        for p in sorted(root.glob(pattern)):
            raw=p.read_bytes()
            try: original=raw.decode('utf-8')
            except UnicodeDecodeError: continue
            repaired=fix_format(original)
            if repaired==original: continue
            diff=''.join(difflib.unified_diff(original.splitlines(True),repaired.splitlines(True),fromfile=p.name,tofile='repaired/'+p.name))
            changes.append({'file':p.name,'before_sha256':digest(raw),'after_sha256':digest(repaired.encode()),'kind':'FORMAT_ONLY','diff':diff})
            if apply:
                target=output/'repaired'/p.name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(repaired,encoding='utf-8')
    result={'kind':'QA_TRIAGE_AND_SAFE_REPAIR','roles':{k:{'name':v[0],'gate':v[1]} for k,v in ROLES.items()},
            'source_root':str(root),'mode':'APPLY_TO_COPIES' if apply else 'DRY_RUN',
            'source_files_untouched':True,'findings':findings,'proposed_format_repairs':changes,
            'semantic_auto_fixes':0,'acceptance':'NOT_VERIFIED',
            'note':'Format-only edits never close semantic, asset, image or video findings; human review and re-audit required.'}
    (output/'qa-repair-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',required=True);a.add_argument('--output',required=True);a.add_argument('--apply-safe',action='store_true');n=a.parse_args()
    r=run(n.root,n.output,n.apply_safe)
    print(json.dumps({'mode':r['mode'],'findings':len(r['findings']),'format_repairs':len(r['proposed_format_repairs']),'acceptance':r['acceptance']},ensure_ascii=False))
