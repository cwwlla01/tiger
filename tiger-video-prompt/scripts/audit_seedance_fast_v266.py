#!/usr/bin/env python3
"""V2.66: textual event order and persistent Take-state handoff preflight.

Uses V2.65 source/hash/witness and V2.64 timing/channel checks. It proves
only declared quotes and ordering, not screenplay semantics, duration accuracy,
channel execution, render quality, or authorized creative rearrangement.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from audit_seedance_fast_v265 import audit as v265, read_source, shot_segment


def locations(haystack, needle):
    if not isinstance(haystack, str) or not isinstance(needle, str) or len(needle.strip()) < 4:
        return []
    out=[]
    start=0
    while True:
        i=haystack.find(needle,start)
        if i<0:break
        out.append(i)
        start=i+1
    return out


def audit(plan):
    base=v265(plan)
    errors=list(base.get('errors',[]))
    notices=list(base.get('notices',[]))
    if plan.get('intent')!='seedance_prompt':
        return {'status':'FAIL' if errors else 'TEXT_STRUCTURE_PASS','errors':errors,'notices':notices,
                'scope':'TASK ROUTE ONLY'}

    source=read_source(plan['source_document'],[]) if plan.get('source_document') else None
    director=read_source(plan['director_document'],[]) if plan.get('director_document') else None
    takes=plan.get('takes') or []
    events=plan.get('critical_events') or []
    by_event={e.get('id'):e for e in events if isinstance(e,dict) and isinstance(e.get('id'),str)}
    by_take={t.get('id'): (i,t) for i,t in enumerate(takes) if isinstance(t,dict)}
    groups=plan.get('sequence_groups') or []

    # Explicit groups separate unrelated scenes; no inferred global chronology
    # for arbitrary multi-episode source files. Each source-backed event belongs
    # to one auditable group, including singleton groups for isolated events.
    if source is not None and len(events)>=2 and not groups:
        errors.append('V266-SEQUENCE-GROUP-MISSING: source-backed events need explicit chronology scopes')
    mentioned=[]
    for group in groups:
        if not isinstance(group,dict):
            errors.append('V266-SEQUENCE-GROUP-MALFORMED');continue
        gid=group.get('id','?')
        ids=group.get('event_ids') or []
        if not isinstance(ids,list) or not ids or any(not isinstance(x,str) or x not in by_event for x in ids):
            errors.append(f'{gid} V266-SEQUENCE-UNKNOWN-EVENT');continue
        if len(set(ids))!=len(ids):errors.append(f'{gid} V266-SEQUENCE-DUPLICATE-EVENT')
        mentioned+=ids
        srcpos=[]; promptpos=[]; directorpos=[]
        for eid in ids:
            e=by_event[eid]
            takeinfo=by_take.get(e.get('take_id'))
            if takeinfo is None:
                errors.append(f'{gid} {eid} V266-TAKE-UNKNOWN');continue
            ti,t=takeinfo
            q=e.get('prompt_quote')
            srcq=e.get('source_quote')
            pp=locations(t.get('prompt'),q)
            sp=locations(source,srcq) if source is not None else []
            if len(pp)!=1:
                errors.append(f'{gid} {eid} V266-PROMPT-ANCHOR-AMBIGUOUS: use one unique action witness')
            else:
                promptpos.append((ti,pp[0]))
            if source is not None:
                if len(sp)!=1:
                    errors.append(f'{gid} {eid} V266-SOURCE-ANCHOR-AMBIGUOUS: use one unique source witness')
                else:
                    srcpos.append(sp[0])
            if director is not None and group.get('mode')=='SOURCE_ORDER':
                dp=locations(director,e.get('director_quote'))
                if len(dp)!=1:
                    errors.append(f'{gid} {eid} V266-DIRECTOR-ORDER-WITNESS: distinct 03 action excerpts required')
                else:
                    directorpos.append(dp[0])
            if len(t.get('shot_ids') or [])>1:
                sh=e.get('shot_id')
                if sh not in (t.get('shot_ids') or []):
                    errors.append(f'{gid} {eid} V266-EVENT-SHOT-ID')
                elif not isinstance(q,str) or q not in (shot_segment(t.get('prompt',''),t.get('shot_ids'),sh) or ''):
                    errors.append(f'{gid} {eid} V266-EVENT-WRONG-SHOT')
        mode=group.get('mode')
        if mode=='SOURCE_ORDER':
            if len(srcpos)==len(ids) and srcpos!=sorted(srcpos):
                errors.append(f'{gid} V266-SOURCE-SEQUENCE-REORDERED: manifest contradicts 01 order')
            if len(promptpos)==len(ids) and promptpos!=sorted(promptpos):
                errors.append(f'{gid} V266-PROMPT-SEQUENCE-REVERSED: 05 action order contradicts 01')
            if director is not None and len(directorpos)==len(ids) and directorpos!=sorted(directorpos):
                errors.append(f'{gid} V266-DIRECTOR-SEQUENCE-REVERSED: 03 shot order contradicts 01')
        elif mode=='DIRECTOR_PRESENTATION_REORDER':
            planned=group.get('presentation_event_ids') or []
            if sorted(planned)!=sorted(ids) or planned==ids:
                errors.append(f'{gid} V266-REORDER-NOT-DESCRIBED')
            dq=group.get('director_order_quote')
            if director is None or len(locations(director,dq))!=1:
                errors.append(f'{gid} V266-REORDER-NO-03-EVIDENCE')
            elif not all(x in dq for x in ids) or not any(x in dq for x in ('先','后','插叙','倒叙','交叉','重排')):
                errors.append(f'{gid} V266-REORDER-03-QUOTE-DOES-NOT-DESCRIBE-ORDER')
            if len(srcpos)==len(ids) and srcpos!=sorted(srcpos):
                errors.append(f'{gid} V266-REORDER-SOURCE-DECLARATION-OUT-OF-ORDER')
            if len(promptpos)==len(ids):
                actual=[x for _,x in sorted(zip(promptpos,ids))]
                if actual!=planned:errors.append(f'{gid} V266-REORDER-PROMPT-DOES-NOT-FOLLOW-03')
            notices.append(f'{gid} V266-REORDER-SEMANTICS-HUMAN-GATE: film presentation order does not authorize physical causality changes')
        else:
            errors.append(f'{gid} V266-UNKNOWN-SEQUENCE-MODE')
    if groups:
        wanted=[e.get('id') for e in events if isinstance(e,dict)]
        if len(mentioned)!=len(wanted) or set(mentioned)!=set(wanted) or len(mentioned)!=len(set(mentioned)):
            errors.append('V266-SEQUENCE-COVERAGE: events must appear exactly once across declared scopes')

    # Generation Takes form an edit sequence, not necessarily one-to-one SHs.
    # Each continuous boundary needs evidence for entry/exit state. A story
    # scene change is separately allowed with a visible 03 source reason.
    handoffs=plan.get('take_handoffs') or []
    if len(takes)>1:
        if len(handoffs)!=len(takes)-1:
            errors.append('V266-HANDOFF-COVERAGE: every adjacent Take needs a continuity or scene-change decision')
        carry={}
        for i in range(len(takes)-1):
            prev,nxt=takes[i],takes[i+1]
            # Most recent declared persistent state effect wins within this Take.
            own=[e for e in events if isinstance(e,dict) and e.get('take_id')==prev.get('id')]
            own.sort(key=lambda e:locations(prev.get('prompt'),e.get('prompt_quote'))[0]
                     if len(locations(prev.get('prompt'),e.get('prompt_quote')))==1 else float('inf'))
            for e in own:
                for key,value in (e.get('state_effects') or {}).items():
                    if not isinstance(key,str) or not isinstance(value,str) or not key.strip() or not value.strip():
                        errors.append(f'{e.get("id")} V266-STATE-EFFECT-MALFORMED')
                    else:carry[key]=value.strip()
            if i>=len(handoffs):continue
            b=handoffs[i]
            tag=f'{prev.get("id")}->{nxt.get("id")}'
            if not isinstance(b,dict) or b.get('from_take')!=prev.get('id') or b.get('to_take')!=nxt.get('id'):
                errors.append(f'{tag} V266-HANDOFF-ORDER');continue
            if b.get('kind')=='SCENE_CHANGE':
                dq=b.get('director_quote')
                if director is not None and len(locations(director,dq))!=1:
                    errors.append(f'{tag} V266-SCENE-CHANGE-NO-DIRECTOR-SOURCE')
                if not isinstance(b.get('reason'),str) or len(b['reason'].strip())<12:
                    errors.append(f'{tag} V266-SCENE-CHANGE-NO-REASON')
                if director is None and source is not None:
                    sq=b.get('source_scene_quote')
                    if len(locations(source,sq))!=1 or not re.search(r'(?:SC\d+|INT\.|EXT\.|内景|外景)',sq or '',re.I):
                        errors.append(f'{tag} V266-SCENE-CHANGE-NO-SOURCE-ANCHOR')
                if director is None and source is None:
                    notices.append(f'{tag} V266-SCENE-CHANGE-CANDIDATE: no 01/03 authority')
            elif b.get('kind')!='CONTINUOUS':
                errors.append(f'{tag} V266-HANDOFF-KIND');continue
            props=b.get('properties') or []
            if not props and b.get('kind')=='CONTINUOUS':
                errors.append(f'{tag} V266-HANDOFF-EMPTY: cannot claim continuity without witnessed state')
            seen_keys=set()
            for p in props:
                if not isinstance(p,dict):errors.append(f'{tag} V266-HANDOFF-PROPERTY-FORM');continue
                key=p.get('key')
                if not isinstance(key,str) or not key.strip() or key in seen_keys:
                    errors.append(f'{tag} V266-HANDOFF-PROPERTY-ID');continue
                seen_keys.add(key)
                end,next_start=p.get('end_value'),p.get('next_start_value')
                if not isinstance(end,str) or not isinstance(next_start,str) or not end.strip() or end!=next_start:
                    errors.append(f'{tag} {key} V266-HANDOFF-STATE-DRIFT')
                for stage,txt,quote in (('END',prev.get('prompt'),p.get('end_quote')),
                                        ('START',nxt.get('prompt'),p.get('next_quote'))):
                    if len(locations(txt,quote))!=1:
                        errors.append(f'{tag} {key} V266-HANDOFF-{stage}-NOT-IN-COPY')
                if key in carry and carry[key]!=end:
                    errors.append(f'{tag} {key} V266-HANDOFF-FACT-DRIFT: persistent story state was lost')
            offscreen=b.get('offscreen_keys') or [] if b.get('kind')=='SCENE_CHANGE' else []
            if (not isinstance(offscreen,list) or any(not isinstance(key,str) or not key for key in offscreen)
                or len(offscreen)!=len(set(offscreen))):
                errors.append(f'{tag} V266-SCENE-OFFSCREEN-KEYS-MALFORMED')
                offscreen=[]
            if set(offscreen)&seen_keys:
                errors.append(f'{tag} V266-STATE-BOTH-ONSCREEN-AND-OFFSCREEN')
            for key,value in carry.items():
                if key not in seen_keys and key not in offscreen:
                    code='V266-SCENE-STATE-OMITTED' if b.get('kind')=='SCENE_CHANGE' else 'V266-HANDOFF-FACT-OMITTED'
                    errors.append(f'{tag} {key} {code}: persistent effect must be visibly carried or explicitly kept offscreen')
            if offscreen:
                notices.append(f'{tag} V266-OFFSCREEN-STATE-UNOBSERVED: values remain in continuity ledger, not visible in this Take')
    elif handoffs:
        errors.append('V266-HANDOFF-UNNECESSARY: single Take has no between-Take boundary')

    return {'status':'FAIL' if errors else 'TEXT_STRUCTURE_PASS',
            'errors':list(dict.fromkeys(errors)), 'notices':list(dict.fromkeys(notices)),
            'edit_total_seconds':base.get('edit_total_seconds'),
            'scope':'REAL SOURCE QUOTE ORDER + TEXT-STATE HANDOFF ONLY; ART, AUTHORITY, UI, RENDER STILL UNVERIFIED'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('plan_json');ap.add_argument('--json-out')
    args=ap.parse_args()
    data=json.loads(Path(args.plan_json).read_text(encoding='utf-8'))
    for field in ('source_document','director_document'):
        ref=data.get(field)
        if isinstance(ref,dict) and isinstance(ref.get('path'),str) and ref['path'] and not Path(ref['path']).is_absolute():
            ref['path']=str((Path(args.plan_json).resolve().parent/ref['path']).resolve())
    result=audit(data)
    output=json.dumps(result,indent=2,ensure_ascii=False)
    print(output)
    if args.json_out:Path(args.json_out).write_text(output+'\n',encoding='utf-8')
    return int(result['status']=='FAIL')

if __name__=='__main__':raise SystemExit(main())
