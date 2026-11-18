#!/usr/bin/env python3
"""Validate provenance and consistency of externally supplied rehearsal logs.

No log, even a passing log, proves a real performer or recording exists.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
from verify_timing_plan import verify


def audit(script, plan, log):
    plan_result = verify(script, plan)
    raw = Path(script).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    plan_bytes = Path(plan).read_bytes()
    plan_hash = hashlib.sha256(plan_bytes).hexdigest()
    doc = json.loads(Path(log).read_text(encoding='utf-8'))
    issues = []
    if not plan_result['plan_screening_pass']:
        issues.append('PLAN_NOT_VALID')
    if doc.get('episode') != plan_result['episode'] or doc.get('script_sha256') != digest or doc.get('plan_sha256') != plan_hash:
        issues.append('SOURCE_MISMATCH')
    if doc.get('status') != 'performed':
        issues.append('NOT_PERFORMED')
    takes = doc.get('takes')
    if not isinstance(takes, list) or len(takes) < 2:
        issues.append('INSUFFICIENT_TAKES')
        takes = takes if isinstance(takes, list) else []
    scene_count = len(plan_result['scenes'])
    seen_ids = set()
    seen_evidence = set()
    passing = []
    take_details = []
    for i,t in enumerate(takes):
        errors = []
        if not isinstance(t,dict):
            errors.append('INVALID_TAKE');t={}
        tid = t.get('take_id')
        if not isinstance(tid,str) or not tid.strip() or tid in seen_ids:
            errors.append('TAKE_ID_INVALID_OR_DUPLICATE')
        seen_ids.add(tid)
        stamp = t.get('performed_at')
        try:
            when = datetime.fromisoformat(stamp) if isinstance(stamp,str) else None
            if when is None or when.tzinfo is None or when.utcoffset() is None:
                raise ValueError('offset-aware ISO datetime required')
        except (ValueError,TypeError):
            errors.append('INVALID_PERFORMED_AT')
        if not isinstance(t.get('operator'),str) or len(t['operator'].strip()) < 2:
            errors.append('MISSING_OPERATOR')
        if t.get('measurement_method') not in ('stopwatch', 'video_timecode', 'audio_timecode'):
            errors.append('UNSUPPORTED_MEASUREMENT_METHOD')
        ev = t.get('evidence_reference')
        if not isinstance(ev,str) or len(ev.strip()) < 8:
            errors.append('MISSING_EVIDENCE_REFERENCE')
        elif ev.strip() in seen_evidence:
            errors.append('DUPLICATE_EVIDENCE_REFERENCE')
        if isinstance(ev,str):
            seen_evidence.add(ev.strip())
        scenes = t.get('scene_seconds')
        if not isinstance(scenes,list) or len(scenes)!=scene_count or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in scenes):
            errors.append('INVALID_SCENE_TIMINGS')
            scenes=[]
        extras = t.get('transitions_and_pauses_seconds')
        if type(extras) not in (int,float) or not math.isfinite(extras) or extras<0:
            errors.append('INVALID_TRANSITION_TIME')
            extras=0
        cut = t.get('omitted_script_content')
        if type(cut) is not bool:
            errors.append('OMISSIONS_NOT_DECLARED')
        elif cut:
            errors.append('SCRIPT_CONTENT_OMITTED')
        if t.get('all_physical_actions_performed') is not True:
            errors.append('ACTIONS_NOT_CONFIRMED')
        if t.get('all_dialogue_performed') is not True:
            errors.append('DIALOGUE_NOT_CONFIRMED')
        if t.get('overlap_safety_checked') is not True:
            errors.append('OVERLAP_SAFETY_NOT_CONFIRMED')
        total = round(sum(scenes)+extras,2) if scenes else None
        if total is not None and not (90<=total<=150):
            errors.append('RUNTIME_OUT_OF_RANGE')
        take_details.append({'take_id':tid,'measured_seconds':total,'issues':errors})
        if not errors: passing.append(total)
        else: issues.append(f'TAKE{i+1}_INVALID')
    # A log cannot establish that the recordings, operators or performances are authentic.
    # In particular, separate references are not evidence that the referenced assets exist.
    # Two separately recorded complete takes, not merely one selected best take.
    accepted = not issues and len(passing)>=2
    return {'episode':plan_result['episode'],'script_sha256':digest,'plan_sha256':plan_hash,
            'planned_seconds':plan_result['planned_screen_seconds'],
            'take_results':take_details,'mechanically_accepted':accepted,'issues':issues,
            'measured_runtime_seconds':passing if accepted else None,
            'warning':'Metadata consistency is not proof the performance occurred, evidence is authentic, or dramatic quality passed. Independent review required.'}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('plan');p.add_argument('log');p.add_argument('--output');a=p.parse_args()
    result=audit(a.script,a.plan,a.log)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(payload,encoding='utf-8')
    print(payload)
    raise SystemExit(0 if result['mechanically_accepted'] else 2)
