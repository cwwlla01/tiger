#!/usr/bin/env python3
"""Separate QA of V2.59 Seedance2Fast Take+POST source coverage, timing and evidence.
No import from producer's validator; no claim to aesthetic/model/video verification.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def seconds(s):
    m, n = s.strip().split(':'); return 60*int(m)+float(n)


def norm_ids(s):
    return [x.upper().replace('-','').replace('_','') for x in re.findall(r'SH[-_]?\d{1,4}',s or '', re.I)]


def field(section, name):
    m = re.search(r'^\*\*'+re.escape(name)+r'\*\*[：:]\s*(.*)$',section,re.M)
    return m.group(1).strip() if m else ''


def duration(v):
    m = re.search(r'(\d+(?:\.\d+)?)秒',v)
    return float(m.group(1)) if m else None


def review(file, source_ids):
    txt=Path(file).read_text(encoding='utf-8')
    parts=list(re.finditer(r'^##\s+(T[-\w]+|POST\d+)\s*[｜|]',txt,re.M))
    issues=[]; captured=[]; total=0.; take_total=0.; post_total=0.
    def error(msg): issues.append(msg)
    header=txt[:parts[0].start()] if parts else txt
    if not parts: error('Q-EMPTY: 无生成/后期单元')
    if not re.fullmatch(r'Seedance\s*2(?:\.0)?\s*Fast',field(header,'模型'),re.I): error('Q-MODEL')
    for i,m in enumerate(parts):
        uid=m.group(1)
        section=txt[m.end():parts[i+1].start() if i+1<len(parts) else len(txt)]
        mapped=norm_ids(field(section,'编辑镜头'))
        captured+=mapped
        blocks=re.findall(r'```text\s*\n(.*?)\n```',section,re.S|re.I)
        if uid.startswith('POST'):
            sec=duration(field(section,'剪辑时长'))
            if len(mapped)!=1 or sec is None or sec<=0 or blocks:
                error(uid+' Q-POST-FORMAT')
            if not field(section,'后期处理') or not field(section,'声画规则'):
                error(uid+' Q-POST-EVIDENCE')
            post_total+=sec or 0
            continue
        g=duration(field(section,'生成时长')); r=duration(field(section,'剪辑保留'))
        k=re.search(r'^(\d{2}:\d{2}(?:\.\d+)?)[-–—~至](\d{2}:\d{2}(?:\.\d+)?)$',field(section,'剪辑截取'))
        if len(blocks)!=1 or not field(section,'合并决策') or not field(section,'素材状态'):
            error(uid+' Q-TAKE-FORMAT')
        if g is None or r is None or g<4 or g>15 or r<=0 or r>g:
            error(uid+' Q-TIME-META')
        if not k or r is None or g is None or abs((seconds(k.group(2))-seconds(k.group(1)))-r)>.06 or seconds(k.group(2))>g+.06:
            error(uid+' Q-KEEP-REGION')
        take_total+=r or 0
        if len(blocks)!=1: continue
        b=blocks[0]
        spans=list(re.finditer(r'【(\d{2}:\d{2}(?:\.\d+)?)[-–—~至](\d{2}:\d{2}(?:\.\d+)?)[｜|](SH[-_]?\d{1,4})[｜|]镜头(\d+)】',b,re.I))
        inner=[x.group(3).upper().replace('-','').replace('_','') for x in spans]
        if inner!=mapped: error(uid+' Q-SHOT-MAP')
        prev=0.
        for j,s in enumerate(spans):
            a,z=seconds(s.group(1)),seconds(s.group(2))
            if abs(a-prev)>.06 or z<=a or int(s.group(4))!=j+1: error(uid+' Q-SPAN-TIME')
            prev=z
            portion=b[s.end():spans[j+1].start() if j+1<len(spans) else len(b)]
            if j and not re.match(r'^\s*(?:硬切|匹配切|遮挡转场|连续运镜|溶解|动作匹配切)\s*[。；:：，,]|^\s*剪辑：',portion):
                error(uid+' Q-CUT')
            for key in ('摄影机：','构图：','光线：','动作：','声音：'):
                if key not in portion: error(uid+' Q-PER-SHOT-'+key)
        if g is not None and (not spans or abs(prev-g)>.06): error(uid+' Q-GEN-TAIL')
        if k:
            active=[s.group(3).upper().replace('-','').replace('_','') for s in spans
                    if min(seconds(s.group(2)),seconds(k.group(2)))-max(seconds(s.group(1)),seconds(k.group(1)))>.06]
            if active!=mapped: error(uid+' Q-EDIT-COVERAGE')
        if any(t in b for t in ('PLACEHOLDER','待核验','见03','@图片1','@图片2')):
            error(uid+' Q-UNVERIFIED-INPUT')
    expected=norm_ids(source_ids)
    if not expected or captured!=expected: error('Q-SOURCE-COVERAGE: '+str({'expected':expected,'actual':captured}))
    declared=duration(field(header,'剪辑总时长'))
    total=take_total+post_total
    if declared is None or abs(total-declared)>.06: error('Q-FINAL-TIME')
    return {'status':'INDEPENDENT_STRUCTURE_PASS' if not issues else 'INDEPENDENT_STRUCTURE_FAIL',
            'issues':issues,'shot_sequence':captured,'take_kept_seconds':take_total,'post_seconds':post_total,
            'final_seconds':total,'scope':'TEXT_STRUCTURE_ONLY; SOURCE_AND_ART_QA_STILL_MANUAL; NO_VIDEO_OBSERVED'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompt',required=True)
    p.add_argument('--expected-shots',required=True)
    p.add_argument('--json-out')
    args=p.parse_args(); result=review(args.prompt,args.expected_shots)
    out=json.dumps(result,ensure_ascii=False,indent=2)
    print(out)
    if args.json_out: Path(args.json_out).write_text(out+'\n',encoding='utf-8')
    return bool(result['issues'])

if __name__=='__main__':sys.exit(main())
