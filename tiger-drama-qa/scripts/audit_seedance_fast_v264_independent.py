#!/usr/bin/env python3
"""Independent V2.64 preflight. Uses neither producer V2.64 nor its helper code."""
import argparse
import json
import math
import re
from pathlib import Path
from audit_seedance_fast_v263_independent import audit as check_route


def number(x):
    return type(x) in (float,int) and math.isfinite(x)


def audit(doc):
    prior=check_route(doc)
    faults=list(prior['errors'])
    if doc.get('intent')!='seedance_prompt':
        return {'status':'FAIL' if faults else 'TEXT_STRUCTURE_PASS','errors':faults,'scope':'ROUTING_ONLY'}
    model=(doc.get('channel') or {}).get('model_display_name','')
    if not re.search(r'seedance\s*2(?:\.0)?\s*fast\b',model,re.I):
        faults.append('QA264-EXACT-FAST-MODEL: do not substitute another Seedance edition')
    style=doc.get('narrative_style','NATURAL')
    if style not in ('NATURAL','PUPPET_STRUCTURAL','PUPPET_MODERATE','PUPPET_FULL_REQUESTED'):
        faults.append('QA264-STYLE-MODE')
    if style!='NATURAL' and doc.get('narrative_style_source') not in ('user_request','approved_project'):
        faults.append('QA264-STYLE-AUTHORISATION')
    final=0
    for take in doc.get('takes',[]):
        id_=take.get('id','?')
        duration=take.get('generated_seconds')
        if not number(duration) or duration<=0:
            faults.append(str(id_)+' QA264-GENERATION-DURATION')
            continue
        keep=(take.get('edit_in_seconds',0),take.get('edit_out_seconds',duration))
        if not all(number(x) for x in keep) or not 0<=keep[0]<keep[1]<=duration:
            faults.append(str(id_)+' QA264-TRIM-BOUNDS')
            continue
        final+=keep[1]-keep[0]
        shot_ids=take.get('shot_ids') or []
        spans=take.get('shot_timeline') or []
        if len(shot_ids)==1 and not spans:
            spans=[{'shot_id':shot_ids[0],'start':0,'end':duration}]
        payoffs=take.get('visible_payoffs') or []
        if [p.get('shot_id') for p in payoffs]!=shot_ids:
            faults.append(str(id_)+' QA264-PAYOFF-ALL-SH')
        for p in payoffs:
            when=p.get('at_seconds')
            matching=[x for x in spans if x.get('shot_id')==p.get('shot_id')]
            if not number(when) or len(matching)!=1 or not all(number(x.get(f)) for x in matching for f in ('start','end')):
                faults.append(str(id_)+' QA264-PAYOFF-INTERVAL')
            else:
                sh=matching[0]
                if when<keep[0]-.001 or when>keep[1]+.001 or when<sh['start']-.001 or when>sh['end']+.001:
                    faults.append(str(id_)+' QA264-PAYOFF-TRIMMED')
            if not isinstance(p.get('visible_result'),str) or len(p['visible_result'].strip())<8:
                faults.append(str(id_)+' QA264-PAYOFF-OBSERVABILITY')
        prompt=take.get('prompt') or ''
        if isinstance(prompt,str):
            if re.search(r'(旁白|诗号|吟诗)\s*[：:]|\bVOICEOVER\s*:',prompt,re.I) and not take.get('source_approved_voiceover'):
                faults.append(str(id_)+' QA264-UNAUTHORISED-VOICE')
            if re.search(r'(画面文字|字幕)\s*[：:]',prompt) and not take.get('source_approved_onscreen_text'):
                faults.append(str(id_)+' QA264-UNAUTHORISED-TEXT')
    for post in doc.get('post_units') or []:
        d=post.get('duration_seconds')
        if not number(d) or d<0: faults.append('QA264-POST-DURATION')
        else: final+=d
    requested=(doc.get('duration_policy') or {}).get('selected_seconds')
    if number(requested) and abs(final-requested)>.06:
        faults.append('QA264-FINAL-CUT-LENGTH')
    return {'status':'FAIL' if faults else 'TEXT_STRUCTURE_PASS', 'errors':list(dict.fromkeys(faults)),
            'retained_seconds':round(final,3), 'scope':'MANIFEST_ONLY; CHANNEL_REALITY_AND_ART_UNVERIFIED'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan_json');p.add_argument('--json-out')
    a=p.parse_args();res=audit(json.loads(Path(a.plan_json).read_text(encoding='utf-8')))
    out=json.dumps(res,ensure_ascii=False,indent=2);print(out)
    if a.json_out:Path(a.json_out).write_text(out+'\n',encoding='utf-8')
    return int(res['status']=='FAIL')

if __name__=='__main__':raise SystemExit(main())
