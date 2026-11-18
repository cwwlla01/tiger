#!/usr/bin/env python3
"""Evidence-anchored semantic patch proposals; optionally write isolated copies, never source."""
import argparse, hashlib, json, difflib
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def run(root, tickets, output, apply=False):
    root=Path(root).resolve(); output=Path(output).resolve()
    if output==root or not output.is_relative_to(root) and root.is_relative_to(output):
        raise ValueError('unsafe output path')
    items=json.loads(Path(tickets).read_text(encoding='utf-8'))
    if isinstance(items,dict): items=items.get('tickets',[])
    if not isinstance(items,list): raise ValueError('tickets must be a list')
    results=[]; staged={}
    for i,t in enumerate(items):
        row={'ticket_id':t.get('id',f'#{i}'),'status':'BLOCKED','role':'independent_reviewer'}
        try:
            rel=Path(t['file'])
            if rel.is_absolute() or '..' in rel.parts or len(rel.parts)!=1 or not rel.name.startswith(('02-','04-','05-')) or rel.suffix!='.md': raise ValueError('not an allowed 02/04/05 markdown file')
            p=(root/rel).resolve()
            if not p.is_relative_to(root) or not p.is_file(): raise ValueError('missing or unsafe file')
            original=p.read_text(encoding='utf-8'); before=sha(p.read_bytes())
            if t.get('source_sha256')!=before: raise ValueError('source hash mismatch')
            old=t['old']; new=t['new']
            if not old or old==new or original.count(old)!=1: raise ValueError('old quote must match exactly once')
            if not new.strip(): raise ValueError('empty replacement')
            if not t.get('source_evidence') or not t.get('rationale') or not t.get('owner'): raise ValueError('missing evidence/rationale/owner')
            if rel.name in staged: raise ValueError('multiple edits to same file require rebase')
            revised=original.replace(old,new,1); staged[rel.name]=revised
            row.update(status='PROPOSED',file=rel.name,owner=t['owner'],source_evidence=t['source_evidence'],rationale=t['rationale'],before_sha256=before,after_sha256=sha(revised.encode()),diff=''.join(difflib.unified_diff(original.splitlines(True),revised.splitlines(True),fromfile=rel.name,tofile='candidate/'+rel.name)))
            if apply:
                target=output/'candidates'/rel.name; target.parent.mkdir(parents=True,exist_ok=True);target.write_text(revised,encoding='utf-8');row['status']='CANDIDATE_WRITTEN_NEEDS_INDEPENDENT_REVIEW'
        except (KeyError,TypeError,ValueError,OSError,UnicodeError) as e: row['reason']=str(e)
        results.append(row)
    output.mkdir(parents=True,exist_ok=True)
    report={'kind':'SEMANTIC_REPAIR_PROPOSALS','source_untouched':True,'acceptance':'NOT_VERIFIED','tickets':results,'note':'Candidate copies are not approved or closed. Re-run full relevant QA gates and independent review.'}
    (output/'semantic-repair-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',required=True);a.add_argument('--tickets',required=True);a.add_argument('--output',required=True);a.add_argument('--write-candidates',action='store_true');n=a.parse_args()
    r=run(n.root,n.tickets,n.output,n.write_candidates)
    print(json.dumps({'proposed':sum(x['status']!='BLOCKED' for x in r['tickets']),'blocked':sum(x['status']=='BLOCKED' for x in r['tickets']),'acceptance':r['acceptance']},ensure_ascii=False))
