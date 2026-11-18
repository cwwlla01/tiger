#!/usr/bin/env python3
"""Independently parse V2.60 key-picture timing against retained ranges.

This implementation does not import the producer's validators. It checks
machine-verifiable directives only, not cinematic quality or model results.
"""
import argparse
import json
import re
from pathlib import Path


def seconds(raw):
    a,b=raw.split(':'); return float(a)*60+float(b)

def normalize(s):
    return s.replace('-','').replace('_','').upper()

def review(path, expected):
    data=Path(path).read_text(encoding='utf-8')
    parts=list(re.finditer(r'^##\s+(T[-\w]+|POST\d+)\s*[｜|]',data,re.M))
    problems=[]; marks=[]; covered=[]
    absolute_cursor=0.0
    for k,hit in enumerate(parts):
        uid=hit.group(1)
        body=data[hit.end():parts[k+1].start() if k+1<len(parts) else len(data)]
        film=re.search(r'^\*\*成片位置\*\*[：:]\s*(\d\d:\d\d(?:\.\d+)?)[-–—~至](\d\d:\d\d(?:\.\d+)?)',body,re.M)
        dur=re.search(r'^\*\*'+('剪辑时长' if uid.startswith('POST') else '剪辑保留')+r'\*\*[：:]\s*(\d+(?:\.\d+)?)秒',body,re.M)
        if not film or not dur:
            problems.append(uid+' Q-ABSOLUTE-MISSING');continue
        start,finish=seconds(film.group(1)),seconds(film.group(2))
        if abs(start-absolute_cursor)>.06 or abs(finish-start-float(dur.group(1)))>.06:
            problems.append(uid+' Q-ABSOLUTE-DURATION')
        absolute_cursor=finish
    top=data[:parts[0].start()] if parts else data
    declared=re.search(r'^\*\*剪辑总时长\*\*[：:]\s*(\d+(?:\.\d+)?)秒',top,re.M)
    if not declared or abs(absolute_cursor-float(declared.group(1)))>.06:
        problems.append('Q-ABSOLUTE-TAIL')
    for k,hit in enumerate(parts):
        unit=hit.group(1)
        if unit.startswith('POST'):
            continue
        body=data[hit.end():parts[k+1].start() if k+1<len(parts) else len(data)]
        mkeep=re.search(r'^\*\*剪辑截取\*\*[：:]\s*(\d\d:\d\d(?:\.\d+)?)[-–—~至](\d\d:\d\d(?:\.\d+)?)',body,re.M)
        if not mkeep:
            problems.append(unit+' Q-MISSING-KEEP'); continue
        lo,hi=seconds(mkeep.group(1)),seconds(mkeep.group(2))
        blocks=re.findall(r'```text\s*\n(.*?)\n```',body,re.S|re.I)
        if len(blocks)!=1:
            problems.append(unit+' Q-BLOCK-COUNT'); continue
        t=blocks[0]
        intervals=list(re.finditer(r'【(\d\d:\d\d(?:\.\d+)?)-(\d\d:\d\d(?:\.\d+)?)[｜|](SH[-_]?\d+)[｜|]镜头\d+】',t,re.I))
        cues=list(re.finditer(r'【(\d\d:\d\d(?:\.\d+)?)[｜|](SH[-_]?\d+)[｜|]关键画面】([^\n【]{9,})',t,re.I))
        if len(cues)!=len(intervals):problems.append(unit+' Q-CUE-COUNT')
        for j, iv in enumerate(intervals):
            tag=normalize(iv.group(3)); covered.append(tag)
            until=intervals[j+1].start() if j+1<len(intervals) else len(t)
            local=[c for c in cues if iv.end()<c.start()<until]
            if len(local)!=1:
                problems.append(unit+' Q-CUE-PER-SHOT '+tag);continue
            c=local[0]; pt=seconds(c.group(1))
            if normalize(c.group(2))!=tag:problems.append(unit+' Q-WRONG-CUE-IDENTITY '+tag)
            if not seconds(iv.group(1))<=pt<=seconds(iv.group(2)):
                problems.append(unit+' Q-CUE-OUTSIDE-SPAN '+tag)
            if not lo<=pt<=hi-.10:
                problems.append(unit+' Q-CUE-CUT-OFF '+tag)
            marks.append([unit,tag,pt])
    expected_ids=[normalize(x) for x in re.findall(r'SH[-_]?\d+',expected,re.I)]
    # The base independent V2.59 gate covers POST-only source events.
    if not expected_ids: problems.append('Q-NO-EXPECTED-SOURCE')
    if len(marks) + len([p for p in parts if p.group(1).startswith('POST')]) != len(expected_ids):
        problems.append('Q-SHOT-COVERAGE')
    return {'status':'INDEPENDENT_TIMING_PASS' if not problems else 'INDEPENDENT_TIMING_FAIL',
            'issues':problems,'visible_key_frame_directives':marks,
            'scope':'DIRECTOR_TIMING_TEXT_ONLY; NO_PIXEL_OR_MODEL_TEST'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prompt',required=True);parser.add_argument('--expected-shots',required=True);parser.add_argument('--json-out')
    a=parser.parse_args();r=review(a.prompt,a.expected_shots)
    out=json.dumps(r,ensure_ascii=False,indent=2);print(out)
    if a.json_out:Path(a.json_out).write_text(out+'\n',encoding='utf-8')
    return bool(r['issues'])

if __name__=='__main__':raise SystemExit(main())
