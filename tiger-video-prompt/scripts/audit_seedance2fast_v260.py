#!/usr/bin/env python3
"""V2.60: verify every SH's visible milestone occurs before the retained edit ends.

Extends V2.59 structural coverage. A key-frame milestone is a *director's timing
instruction*, NOT evidence of a generated frame or successful model compliance.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from audit_seedance2fast_v259 import audit as audit_v259, HEADER, CODE, SPAN, sec, meta, keep_range, length, norm, shots

PAYOFF = re.compile(r'【(\d{2}:\d{2}(?:\.\d+)?)\s*[｜|]\s*(SH[-_]?\d{1,4})\s*[｜|]\s*关键画面】([^\n【]{9,})', re.I)


def audit(path, expected):
    result = audit_v259(path, expected)
    raw = Path(path).read_text(encoding='utf-8')
    headings = list(HEADER.finditer(raw))
    errors = list(result['errors'])
    observations = []
    film_cursor = 0.0
    for i,h in enumerate(headings):
        uid=h.group(1)
        section=raw[h.end():headings[i+1].start() if i+1<len(headings) else len(raw)]
        film=keep_range(meta(section,'成片位置'))
        span=length(meta(section,'剪辑时长' if uid.startswith('POST') else '剪辑保留'))
        if film is None or span is None:
            errors.append(f'{uid} E-FILM-POSITION: 缺成片位置或剪辑时长')
            continue
        if abs(film[0]-film_cursor)>.06:
            errors.append(f'{uid} E-FILM-GAP: 成片起点{film[0]:g}与上一片段结束{film_cursor:g}不连续')
        if abs(film[1]-film[0]-span)>.06:
            errors.append(f'{uid} E-FILM-SPAN: 成片区间与保留秒数不一致')
        film_cursor=film[1]
    declared=length(meta(raw[:headings[0].start()] if headings else raw,'剪辑总时长'))
    if declared is not None and abs(film_cursor-declared)>.06:
        errors.append(f'E-FILM-END: 成片最后时刻{film_cursor:g}与目标{declared:g}不一致')
    for i,h in enumerate(headings):
        uid = h.group(1)
        if uid.startswith('POST'):
            continue
        section = raw[h.end():headings[i + 1].start() if i + 1<len(headings) else len(raw)]
        chunks = CODE.findall(section)
        if len(chunks) != 1:
            continue
        code = chunks[0]
        spans = list(SPAN.finditer(code))
        checkpoints = list(PAYOFF.finditer(code))
        if len(checkpoints) != len(spans):
            errors.append(f'{uid} E-PAYOFF-COUNT: {len(checkpoints)}关键画面 / {len(spans)}镜头')
        kept = keep_range(meta(section,'剪辑截取'))
        for j,sp in enumerate(spans):
            shot = norm(sp.group(3))
            inside_end = spans[j+1].start() if j+1<len(spans) else len(code)
            inside = [p for p in checkpoints if sp.end() < p.start() < inside_end]
            if len(inside)!=1:
                errors.append(f'{uid} E-PAYOFF-SHOT: {shot}关键画面必须且只能出现一次')
                continue
            point = inside[0]
            t = sec(point.group(1))
            if norm(point.group(2)) != shot:
                errors.append(f'{uid} E-PAYOFF-ID: {shot}关键画面属于别的SH')
            if not (sec(sp.group(1)) <= t <= sec(sp.group(2))):
                errors.append(f'{uid} E-PAYOFF-OUTSIDE-SHOT: {shot}@{t:g}')
            if not kept or not (kept[0] <= t <= kept[1] - .10):
                errors.append(f'{uid} E-PAYOFF-TRIMMED: {shot}@{t:g} 未进入实际剪辑保留区间，至少留0.1秒可见余量')
            observations.append({'take':uid,'shot':shot,'payoff_seconds':t,'payoff':' '.join(point.group(3).split())})
    result['errors']=errors
    result['status']='TEXT_STRUCTURE_PASS' if not errors else 'TEXT_STRUCTURE_FAIL'
    result['visible_payoff_checks']=observations
    result['evidence']='TEXT_AND_DIRECTOR_TIMING_DESIGN_ONLY; NOT_VIDEO_FRAME_VERIFICATION'
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prompt_md'); p.add_argument('--expected-shots',required=True); p.add_argument('--json-out')
    a=p.parse_args()
    r=audit(a.prompt_md,a.expected_shots)
    txt=json.dumps(r,ensure_ascii=False,indent=2)
    print(txt)
    if a.json_out: Path(a.json_out).write_text(txt+'\n',encoding='utf-8')
    return int(r['status']!='TEXT_STRUCTURE_PASS')

if __name__=='__main__': raise SystemExit(main())
