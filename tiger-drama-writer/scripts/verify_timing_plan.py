#!/usr/bin/env python3
"""Audit a shot/beat timing PLAN bound to immutable episode text; never certifies measured runtime."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from audit_script_batch import EP, SC, SPEECH, han


def verify(script, plan):
    source = Path(script).read_bytes()
    text = source.decode('utf-8')
    data = json.loads(Path(plan).read_text(encoding='utf-8'))
    issues = []
    digest = hashlib.sha256(source).hexdigest()
    if data.get('sha256') != digest:
        issues.append('SCRIPT_HASH_MISMATCH')
    headings = list(EP.finditer(text))
    if len(headings) != 1 or data.get('episode') != int(headings[0].group(1)):
        issues.append('EPISODE_MISMATCH')
    cuts = list(SC.finditer(text))
    rows = []
    plans = data.get('scenes', [])
    if len(plans) != len(cuts):
        issues.append('SCENE_COUNT_MISMATCH')
    for idx, heading in enumerate(cuts):
        chunk = text[heading.end():cuts[idx+1].start() if idx+1<len(cuts) else len(text)]
        spoken = sum(han(content) for _,_,content in SPEECH.findall(chunk))
        source_lines = [m.group(0).strip() for m in SPEECH.finditer(chunk)]
        stage_lines = [line.strip() for line in chunk.splitlines() if line.lstrip().startswith('△')]
        seen_action_quotes = set()
        last_stage_index = -1
        allocated_lines = []
        scene_plan = plans[idx] if idx < len(plans) else {}
        if scene_plan.get('scene') != idx+1:
            issues.append(f'SCENE{idx+1}_ORDER_MISMATCH')
        beats = scene_plan.get('beats', [])
        if not beats:
            issues.append(f'SCENE{idx+1}_NO_BEATS')
        seconds = 0.0
        speech_secs = 0.0
        independent_action_secs = 0.0
        for j,b in enumerate(beats):
            a,bsp = b.get('action_seconds'),b.get('speech_seconds')
            if type(a) not in (int,float) or type(bsp) not in (int,float) or not (math.isfinite(a) and math.isfinite(bsp)) or a < 0 or bsp < 0:
                issues.append(f'SCENE{idx+1}_BEAT{j+1}_INVALID_SECONDS')
                continue
            if type(b.get('overlap')) is not bool:
                issues.append(f'SCENE{idx+1}_BEAT{j+1}_OVERLAP_UNSPECIFIED')
                continue
            if not b.get('physical_action') or not isinstance(b.get('physical_action'),str):
                issues.append(f'SCENE{idx+1}_BEAT{j+1}_MISSING_ACTION_LABEL')
            # A planned action must cite a real stretch of on-page stage direction.
            action_quote = b.get('action_quote')
            if a > 0:
                if not isinstance(action_quote,str) or len(action_quote.strip()) < 12:
                    issues.append(f'SCENE{idx+1}_BEAT{j+1}_ACTION_NOT_GROUNDED')
                else:
                    matches = [k for k, line in enumerate(stage_lines) if action_quote in line]
                    if not matches:
                        issues.append(f'SCENE{idx+1}_BEAT{j+1}_ACTION_NOT_IN_STAGE_DIRECTION')
                    else:
                        first = matches[0]
                        if first < last_stage_index:
                            issues.append(f'SCENE{idx+1}_BEAT{j+1}_ACTION_ORDER_REVERSED')
                        last_stage_index = first
                    if action_quote in seen_action_quotes:
                        issues.append(f'SCENE{idx+1}_BEAT{j+1}_ACTION_EVIDENCE_REUSED')
                    seen_action_quotes.add(action_quote)
            # Allocate every complete dialogue line to exactly one beat, in script order.
            lines = b.get('speech_lines')
            if not isinstance(lines,list) or any(not isinstance(x,str) for x in lines):
                issues.append(f'SCENE{idx+1}_BEAT{j+1}_DIALOGUE_ALLOCATION_MISSING')
                lines=[]
            allocated_lines.extend(lines)
            beat_han = sum(han(x.split('：',1)[-1].split(':',1)[-1]) for x in lines)
            if bsp + 0.001 < beat_han / 300 * 60:
                issues.append(f'SCENE{idx+1}_BEAT{j+1}_DIALOGUE_TOO_FAST')
            if bsp > 0 and not lines:
                issues.append(f'SCENE{idx+1}_BEAT{j+1}_UNATTRIBUTED_SPEECH_TIME')
            seconds += max(a,bsp) if b['overlap'] else a+bsp
            speech_secs += bsp
            if not b['overlap']:
                independent_action_secs += a
        if allocated_lines != source_lines:
            issues.append(f'SCENE{idx+1}_DIALOGUE_COVERAGE_MISMATCH')
        # Guard against aspirational plans requiring implausibly fast delivery.
        if speech_secs + 0.001 < spoken / 300 * 60:
            issues.append(f'SCENE{idx+1}_SPEECH_TOO_FAST_FOR_PLAN')
        rows.append({'scene':idx+1,'dialogue_han':spoken,'planned_speech_seconds':round(speech_secs,1),
                     'planned_screen_seconds':round(seconds,1),'independent_action_seconds':round(independent_action_secs,1)})
    duration = round(sum(x['planned_screen_seconds'] for x in rows),1)
    if sum(x['independent_action_seconds'] for x in rows) == 0:
        issues.append('ALL_ACTION_TIME_ASSUMED_OVERLAPPED')
    if duration < 90 or duration > 150:
        issues.append('PLAN_OUTSIDE_90_150')
    return {'episode':data.get('episode'),'sha256':digest,'planned_screen_seconds':duration,
            'scenes':rows,'plan_screening_pass':not issues,'issues':sorted(set(issues)),
            'measured_runtime_seconds':None,
            'warning':'This validates declared timing assumptions and a text hash, not whether shots are actable or timed. Require filmed rehearsal or table read.'}

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('script');ap.add_argument('plan');ap.add_argument('--output');args=ap.parse_args()
    out=verify(args.script,args.plan)
    payload=json.dumps(out,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(payload,encoding='utf-8')
    print(payload)
    raise SystemExit(0 if out['plan_screening_pass'] else 2)
