#!/usr/bin/env python3
"""Independent V2.66 chronology/adjacent-Take state preflight.

Does not import producer validators. Exact quote/order and state labels are
structural evidence, NOT semantic, live-channel, asset, or finished-video QA.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from audit_seedance_fast_v265_independent import audit as old_qa


def read_file(doc,kind,problems):
    ref=doc.get(kind)
    if not isinstance(ref,dict):return None
    try:
        f=Path(ref.get('path',''))
        raw=f.read_bytes()
        if len(raw)>8_000_000 or hashlib.sha256(raw).hexdigest()!=ref.get('sha256','').lower():
            raise ValueError('hash')
        return raw.decode('utf-8')
    except (OSError,ValueError,UnicodeError):
        problems.append('QA266-SOURCE-NOT-VERIFIABLE: '+kind)
        return None


def once(text,phrase):
    if not isinstance(text,str) or not isinstance(phrase,str) or len(phrase.strip())<4:return None
    i=text.find(phrase)
    return i if i>=0 and text.find(phrase,i+1)<0 else None


def review(doc):
    base=old_qa(doc)
    problems=list(base.get('errors',[]))
    notes=list(base.get('notices',[]))
    if doc.get('intent')!='seedance_prompt':
        return {'status':'FAIL' if problems else 'TEXT_STRUCTURE_PASS','errors':problems,'notices':notes}
    script=read_file(doc,'source_document',problems)
    director=read_file(doc,'director_document',problems)
    takes=doc.get('takes') or []
    evt={e.get('id'):e for e in doc.get('critical_events') or [] if isinstance(e,dict) and isinstance(e.get('id'),str)}
    takeindex={t.get('id'):i for i,t in enumerate(takes) if isinstance(t,dict)}
    allgroups=doc.get('sequence_groups') or []
    declared=[]
    if script is not None and len(evt)>1 and not allgroups:
        problems.append('QA266-MISSING-ORDER-GROUPS')

    for group in allgroups:
        if not isinstance(group,dict):problems.append('QA266-BAD-GROUP');continue
        title=group.get('id','?')
        ids=group.get('event_ids') or []
        if not ids or len(ids)!=len(set(ids)) or any(x not in evt for x in ids):
            problems.append(str(title)+' QA266-GROUP-CONTENTS');continue
        declared.extend(ids)
        source_positions=[]
        final_positions=[]
        director_positions=[]
        for event_id in ids:
            e=evt[event_id]
            tix=takeindex.get(e.get('take_id'))
            if tix is None:
                problems.append(title+' QA266-BAD-TAKE');continue
            t=takes[tix]
            p=once(t.get('prompt'),e.get('prompt_quote'))
            if p is None:
                problems.append(title+' '+event_id+' QA266-PROMPT-QUOTE-NOT-UNIQUE')
            else:final_positions.append((tix,p))
            if script is not None:
                s=once(script,e.get('source_quote'))
                if s is None: problems.append(title+' '+event_id+' QA266-SOURCE-QUOTE-NOT-UNIQUE')
                else:source_positions.append(s)
            if director is not None and group.get('mode')=='SOURCE_ORDER':
                d=once(director,e.get('director_quote'))
                if d is None:problems.append(title+' '+event_id+' QA266-03-ACTION-NOT-UNIQUE')
                else:director_positions.append(d)
            if len(t.get('shot_ids') or [])>1:
                sid=e.get('shot_id')
                shots=t.get('shot_ids') or []
                if sid not in shots:
                    problems.append(title+' '+event_id+' QA266-SH-UNKNOWN')
                else:
                    # Require event-specific text inside the one tagged SH slice;
                    # a global ending recap is not a valid substitute.
                    spans=list(re.finditer(r'\bSH[-_]?(\d{1,4})\b',t.get('prompt',''),re.I))
                    target='SH'+str(sid).replace('SH','').replace('-','').replace('_','').zfill(2)
                    valid=[]
                    for j,m in enumerate(spans):
                        if 'SH'+m.group(1).zfill(2)==target:
                            valid.append(t.get('prompt','')[m.end():spans[j+1].start() if j+1<len(spans) else len(t.get('prompt',''))])
                    if len(valid)!=1 or not isinstance(e.get('prompt_quote'),str) or e['prompt_quote'] not in valid[0]:
                        problems.append(title+' '+event_id+' QA266-SH-QUOTE-WRONG-LOCATION')
        kind=group.get('mode')
        if kind=='SOURCE_ORDER':
            if len(source_positions)==len(ids) and source_positions!=sorted(source_positions):
                problems.append(title+' QA266-01-ORDER-MISMATCH')
            if len(final_positions)==len(ids) and final_positions!=sorted(final_positions):
                problems.append(title+' QA266-05-ORDER-MISMATCH')
            if director is not None and len(director_positions)==len(ids) and director_positions!=sorted(director_positions):
                problems.append(title+' QA266-03-ORDER-MISMATCH')
        elif kind=='DIRECTOR_PRESENTATION_REORDER':
            planned=group.get('presentation_event_ids') or []
            if len(planned)!=len(ids) or set(planned)!=set(ids) or planned==ids:
                problems.append(title+' QA266-REORDER-MANIFEST')
            phrase=group.get('director_order_quote')
            if once(director,phrase) is None or not all(x in str(phrase) for x in ids) or not any(x in str(phrase) for x in ('先','后','插叙','倒叙','交叉','重排')):
                problems.append(title+' QA266-REORDER-NO-03-DIRECTIVE')
            if len(source_positions)==len(ids) and source_positions!=sorted(source_positions):
                problems.append(title+' QA266-REORDER-01-EVENTS-OUT-OF-ORDER')
            if len(final_positions)==len(ids) and [eid for _,eid in sorted(zip(final_positions,ids))]!=planned:
                problems.append(title+' QA266-REORDER-NOT-IN-05')
            notes.append(title+' QA266-PRESENTATION-REORDER-REQUIRES-MANUAL-SEMANTIC-REVIEW')
        else:problems.append(title+' QA266-UNKNOWN-ORDER-MODE')
    if allgroups and (len(declared)!=len(evt) or len(set(declared))!=len(declared) or set(declared)!=set(evt)):
        problems.append('QA266-CRITICAL-EVENT-GROUP-COVERAGE')

    borders=doc.get('take_handoffs') or []
    if len(takes)==1 and borders:problems.append('QA266-SPURIOUS-TAKE-BORDER')
    if len(takes)>1 and len(borders)!=len(takes)-1:
        problems.append('QA266-TAKE-BORDER-NOT-EXHAUSTIVE')
    persistent={}
    for i in range(max(0,len(takes)-1)):
        left,right=takes[i:i+2]
        source_events=[e for e in evt.values() if e.get('take_id')==left.get('id')]
        source_events.sort(key=lambda e:(once(left.get('prompt'),e.get('prompt_quote')) if once(left.get('prompt'),e.get('prompt_quote')) is not None else 10**10))
        for e in source_events:
            for key,value in (e.get('state_effects') or {}).items():
                if not isinstance(key,str) or not isinstance(value,str) or not key.strip() or not value.strip():
                    problems.append('QA266-INVALID-PERSISTENT-EFFECT')
                else:persistent[key]=value
        if i>=len(borders):continue
        border=borders[i]
        tag=f'{left.get("id")}->{right.get("id")}'
        if not isinstance(border,dict) or border.get('from_take')!=left.get('id') or border.get('to_take')!=right.get('id'):
            problems.append(tag+' QA266-MISORDERED-BORDER');continue
        kind=border.get('kind')
        if kind=='SCENE_CHANGE':
            reason=border.get('reason')
            if not isinstance(reason,str) or len(reason.strip())<12:
                problems.append(tag+' QA266-SCENE-CHANGE-REASON-MISSING')
            if director is not None and once(director,border.get('director_quote')) is None:
                problems.append(tag+' QA266-SCENE-CHANGE-NOT-IN-03')
            if director is None and script is not None:
                sq=border.get('source_scene_quote')
                if once(script,sq) is None or not re.search(r'(?:SC\d+|INT\.|EXT\.|内景|外景)',sq or '',re.I):
                    problems.append(tag+' QA266-SCENE-CHANGE-NOT-IN-01')
            if director is None and script is None:notes.append(tag+' QA266-SCENE-CHANGE-UNVERIFIED')
        elif kind!='CONTINUOUS':
            problems.append(tag+' QA266-BORDER-TYPE');continue
        fields=border.get('properties') or []
        if not fields and kind=='CONTINUOUS':problems.append(tag+' QA266-EMPTY-CONTINUITY')
        covered=set()
        for field in fields:
            if not isinstance(field,dict) or not isinstance(field.get('key'),str):
                problems.append(tag+' QA266-BAD-FIELD');continue
            key=field['key']
            if not key or key in covered:problems.append(tag+' QA266-REPEATED-FIELD')
            covered.add(key)
            val=field.get('end_value')
            if not isinstance(val,str) or not val or val!=field.get('next_start_value'):
                problems.append(tag+' '+key+' QA266-STATE-CHANGES-WITHOUT-TRANSITION')
            if once(left.get('prompt'),field.get('end_quote')) is None:
                problems.append(tag+' '+key+' QA266-NO-END-TEXT')
            if once(right.get('prompt'),field.get('next_quote')) is None:
                problems.append(tag+' '+key+' QA266-NO-NEXT-START-TEXT')
            if key in persistent and val!=persistent[key]:
                problems.append(tag+' '+key+' QA266-SOURCE-EFFECT-LOST')
        offscreen=border.get('offscreen_keys') or [] if kind=='SCENE_CHANGE' else []
        if not isinstance(offscreen,list) or any(not isinstance(k,str) or not k for k in offscreen) or len(offscreen)!=len(set(offscreen)):
            problems.append(tag+' QA266-BAD-OFFSCREEN-KEYS');offscreen=[]
        if set(offscreen)&covered:problems.append(tag+' QA266-VISIBLE-AND-OFFSCREEN-CONFLICT')
        for key in persistent:
            if key not in covered and key not in offscreen:
                code='QA266-SCENE-LOST-PERSISTENT-STATE' if kind=='SCENE_CHANGE' else 'QA266-PERSISTENT-FIELD-OMITTED'
                problems.append(tag+' '+key+' '+code)
        if offscreen:notes.append(tag+' QA266-OFFSCREEN-CARRY-NOT-PIXEL-VERIFIED')

    return {'status':'FAIL' if problems else 'TEXT_STRUCTURE_PASS',
            'errors':list(dict.fromkeys(problems)), 'notices':list(dict.fromkeys(notes)),
            'retained_seconds':base.get('retained_seconds'),
            'scope':'INDEPENDENT TEXT ORDER AND CONTINUITY ONLY; HUMAN REVIEW REQUIRED'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('plan_json');ap.add_argument('--json-out')
    args=ap.parse_args()
    doc=json.loads(Path(args.plan_json).read_text(encoding='utf-8'))
    for n in ('source_document','director_document'):
        ref=doc.get(n)
        if isinstance(ref,dict) and isinstance(ref.get('path'),str) and not Path(ref['path']).is_absolute():
            ref['path']=str((Path(args.plan_json).resolve().parent/ref['path']).resolve())
    r=review(doc)
    out=json.dumps(r,indent=2,ensure_ascii=False)
    print(out)
    if args.json_out:Path(args.json_out).write_text(out+'\n',encoding='utf-8')
    return int(r['status']=='FAIL')

if __name__=='__main__':raise SystemExit(main())
