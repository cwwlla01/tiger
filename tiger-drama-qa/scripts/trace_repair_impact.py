#!/usr/bin/env python3
"""Create an evidence packet and downstream impact list; never approve semantics."""
import argparse, hashlib, json, re
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def trace(root, tickets, candidate_root):
    results=[]
    for t in tickets['tickets']:
        src=root/t['file']; candidate=candidate_root/t['file']
        row={'id':t['id'],'status':'NEEDS_SEMANTIC_REVIEW','checks':{},'evidence':[],'downstream':[],'flags':[]}
        if not src.is_file() or not candidate.is_file():
            row['flags'].append('SOURCE_OR_CANDIDATE_MISSING'); results.append(row);continue
        original=src.read_text(encoding='utf-8'); revised=candidate.read_text(encoding='utf-8')
        row['checks']={'source_hash_matches':sha(src)==t.get('source_sha256'),'old_unique':original.count(t.get('old',''))==1 if t.get('old') else False,'candidate_exact_change':original.replace(t['old'],t['new'],1)==revised if t.get('old') else False}
        for key,ok in row['checks'].items():
            if not ok:row['flags'].append(key.upper()+'_FAILED')
        # Quote actual cited source lines; do not equate citation presence with semantic truth.
        ev=t.get('source_evidence','')
        for m in re.finditer(r'([^\s，；]+\.md)\s*第(\d+)(?:-(\d+))?行',ev):
            path=root/m.group(1); start=int(m.group(2)); end=int(m.group(3) or start)
            if path.is_file() and 0<start<=end<=len(path.read_text(encoding='utf-8').splitlines()) and end-start<=15:
                lines=path.read_text(encoding='utf-8').splitlines()
                row['evidence'].append({'file':path.name,'start':start,'end':end,'actual_excerpt':'\n'.join(f'{i}: {lines[i-1]}' for i in range(start,end+1))})
            else:row['flags'].append('EVIDENCE_LINE_UNAVAILABLE')
        if not row['evidence']:row['flags'].append('NO_VERIFIABLE_LINE_EVIDENCE')
        # Scope impact search to explicitly named asset IDs, not generic nouns.
        ids=sorted(set(re.findall(r'(?:CHAR|MONSTER|SCENE|PROP)-\d{3}', t['id']+' '+ev+' '+t.get('rationale',''))))
        row['asset_ids']=ids
        for prefix in ('03-专业导演分镜.md','04-画面帧生成提示词.md','05-视频生成提示词.md'):
            p=root/prefix
            if not p.is_file():row['flags'].append('DOWNSTREAM_FILE_MISSING:'+prefix);continue
            lines=p.read_text(encoding='utf-8').splitlines()
            hits=[{'line':i,'text':line[:180]} for i,line in enumerate(lines,1) if any(a in line for a in ids)]
            row['downstream'].append({'file':prefix,'hit_count':len(hits),'sample_hits':hits[:12]})
        row['review_questions']=['候选替换是否与实际引用的权威分镜逐行一致？','是否引入未经批准的设计细节？','下游04/05受影响镜头是否重新编译与复验？']
        results.append(row)
    return {'kind':'REPAIR_EVIDENCE_AND_IMPACT','acceptance':'NOT_VERIFIED','tickets':results,'note':'Evidence excerpts and reference hits are routing aids, not independent semantic approval.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--tickets',required=True);ap.add_argument('--candidates',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    result=trace(Path(a.root),json.loads(Path(a.tickets).read_text(encoding='utf-8')),Path(a.candidates))
    p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'tickets':len(result['tickets']),'flags':sum(len(t['flags']) for t in result['tickets']),'acceptance':result['acceptance']},ensure_ascii=False))
if __name__=='__main__':main()
