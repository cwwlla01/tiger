#!/usr/bin/env python3
"""V2.64 current Seedance plan audit. Structural assertions, NOT video QA.

Avoid legacy V2.59/V2.60 format validators for non-fixture scenes. Their historical
15-second examples must not become the current user's implicit duration.
"""
from __future__ import annotations
import argparse
import json
import math
import re
from pathlib import Path
from audit_seedance_fast_v263 import audit as audit_v263

VALID_STYLES={'NATURAL','PUPPET_STRUCTURAL','PUPPET_MODERATE','PUPPET_FULL_REQUESTED'}


def num(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def audit(plan):
    base=audit_v263(plan)
    errors=list(base.get('errors',[]))
    notices=list(base.get('notices',[]))
    intent=plan.get('intent')
    if intent!='seedance_prompt':
        return {'status':'FAIL' if errors else 'TEXT_STRUCTURE_PASS', 'errors':errors, 'notices':notices,
                'scope':'V2.64 routing only, no video produced'}
    style=plan.get('narrative_style','NATURAL')
    if style not in VALID_STYLES:
        errors.append('V264-STYLE: unknown narrative style')
    if style!='NATURAL' and plan.get('narrative_style_source') not in {'user_request','approved_project'}:
        errors.append('V264-STYLE-SOURCE: no actual authorisation for puppet-influenced style')
    total=0.0
    for take in plan.get('takes',[]):
        tid=str(take.get('id','?'))
        g=take.get('generated_seconds')
        if not num(g) or g<=0:
            continue
        start=take.get('edit_in_seconds',0)
        end=take.get('edit_out_seconds',g)
        if not num(start) or not num(end) or not 0<=start<end<=g:
            errors.append(f'{tid} V264-TRIM: invalid local edit boundaries')
            continue
        total+=end-start
        shot_ids=take.get('shot_ids') or []
        payoffs=take.get('visible_payoffs') or []
        if len(payoffs)!=len(shot_ids) or [p.get('shot_id') for p in payoffs]!=shot_ids:
            errors.append(f'{tid} V264-PAYOFF-COVERAGE: every SH must have an ordered result')
        timeline=take.get('shot_timeline') or [{'shot_id':shot_ids[0], 'start':0, 'end':g}] if len(shot_ids)==1 else take.get('shot_timeline') or []
        by_sh={r.get('shot_id'):(r.get('start'),r.get('end')) for r in timeline if isinstance(r,dict)}
        for p in payoffs:
            sh=p.get('shot_id')
            t=p.get('at_seconds')
            visible=p.get('visible_result','')
            interval=by_sh.get(sh)
            if not num(t) or not interval or not all(num(x) for x in interval):
                errors.append(f'{tid} {sh} V264-PAYOFF-POSITION: missing local time interval')
            elif not (interval[0]-0.001<=t<=interval[1]+0.001 and start-0.001<=t<=end+0.001):
                errors.append(f'{tid} {sh} V264-PAYOFF-TRIM: climax does not occur inside the retained shot portion')
            if not isinstance(visible,str) or len(visible.strip())<8:
                errors.append(f'{tid} {sh} V264-PAYOFF-VISIBLE: specify the observable changed state')
        prompt=take.get('prompt') or ''
        if not isinstance(prompt,str):
            continue
        if re.search(r'(?:旁白|诗号|吟诗)\s*[：:]|\bVOICEOVER\s*:',prompt,re.I) and not take.get('source_approved_voiceover',False):
            errors.append(f'{tid} V264-VOICEOVER: narration/poetry not authorised by source')
        if re.search(r'(?:画面文字|字幕)\s*[：:]',prompt) and not take.get('source_approved_onscreen_text',False):
            errors.append(f'{tid} V264-TEXT: unapproved exact text in the model prompt')
    for post in plan.get('post_units') or []:
        sec=post.get('duration_seconds')
        if not num(sec) or sec<0:
            errors.append('V264-POST: invalid standalone editorial duration')
        else:
            total+=sec
    target=(plan.get('duration_policy') or {}).get('selected_seconds')
    if num(target) and abs(total-target)>0.06:
        errors.append(f'V264-FINAL-DURATION: planned {target:g}s, retained takes+post {total:g}s')
    return {'status':'FAIL' if errors else 'TEXT_STRUCTURE_PASS','errors':list(dict.fromkeys(errors)),
            'notices':notices, 'edit_total_seconds':round(total,3),
            'scope':'TEXT_AND_MANIFEST_STRUCTURE_ONLY; NO REAL UI/IMAGE/VIDEO QA'}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('plan_json')
    a.add_argument('--json-out')
    args=a.parse_args()
    result=audit(json.loads(Path(args.plan_json).read_text(encoding='utf-8')))
    out=json.dumps(result,ensure_ascii=False,indent=2)
    print(out)
    if args.json_out: Path(args.json_out).write_text(out+'\n',encoding='utf-8')
    return int(result['status']=='FAIL')

if __name__=='__main__': raise SystemExit(main())
