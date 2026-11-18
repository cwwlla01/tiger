#!/usr/bin/env python3
"""Independent V2.65 audit of exact screenplay and copy-text witnesses.

Independent of producer's V2.65 implementation; still cannot judge meaning,
real video, model UI execution, or whether the user actually approved a style.
"""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from audit_seedance_fast_v264_independent import audit as audit_v264


def exact_text(s, part):
    return isinstance(s,str) and isinstance(part,str) and len(part.strip())>=4 and part in s


def read_declared_source(doc, issues, key='source_document'):
    ref=doc.get(key)
    if ref is None:return None
    if not isinstance(ref,dict) or not isinstance(ref.get('path'),str) or not re.fullmatch(r'[a-fA-F0-9]{64}',str(ref.get('sha256',''))):
        issues.append('QA265-BAD-SOURCE-MANIFEST')
        return None
    try:
        p=Path(ref['path'])
        if not p.is_file() or p.stat().st_size>8_000_000:
            raise ValueError()
        bytes_=p.read_bytes()
        if hashlib.sha256(bytes_).hexdigest().lower()!=ref['sha256'].lower():
            issues.append('QA265-SOURCE-CHANGED')
            return None
        return bytes_.decode('utf-8')
    except (ValueError,OSError,UnicodeError):
        issues.append('QA265-SOURCE-MISSING')
        return None


def has_speech(s):
    return isinstance(s,str) and re.search(r'(?:旁白|诗号|吟诗)\s*[：:]|\bVOICEOVER\s*:',s,re.I) is not None


def shot_chunks(prompt):
    headers=list(re.finditer(r'(?<![\w-])SH[-_]?(\d{1,4})(?!\d)',prompt,re.I))
    spans={}
    for i,h in enumerate(headers):
        key='SH'+h.group(1).zfill(2)
        spans.setdefault(key,[]).append(prompt[h.end():headers[i+1].start() if i+1<len(headers) else len(prompt)])
    return spans


def audit(doc):
    issues=[]
    source=read_declared_source(doc,issues) if doc.get('intent')=='seedance_prompt' else None
    director=read_declared_source(doc,issues,'director_document') if doc.get('intent')=='seedance_prompt' else None
    compatibility=copy.deepcopy(doc)
    for take in compatibility.get('takes',[]) if doc.get('intent')=='seedance_prompt' else []:
        prompt=take.get('prompt')
        if not isinstance(prompt,str):continue
        proof=take.get('voiceover_evidence') or {}
        sq=proof.get('source_quote');pq=proof.get('prompt_quote')
        script_ok=(proof.get('origin')=='script' and source is not None
                   and exact_text(source,sq) and exact_text(prompt,pq)
                   and has_speech(sq) and has_speech(pq))
        user_ok=(proof.get('origin')=='user_request' and has_speech(sq)
                 and exact_text(prompt,pq) and has_speech(pq))
        if script_ok or user_ok:
            take['source_approved_voiceover']=True
        text_proof=take.get('onscreen_text_evidence') or {}
        if source is not None and exact_text(source,text_proof.get('source_quote')) and exact_text(prompt,text_proof.get('prompt_quote')):
            take['source_approved_onscreen_text']=True
    b=audit_v264(compatibility)
    issues.extend(b.get('errors',[]))
    notices=[]
    if doc.get('intent')!='seedance_prompt':
        return {'status':'FAIL' if issues else 'TEXT_STRUCTURE_PASS','errors':issues,
                'scope':'ROUTING_ONLY'}
    if doc.get('source_document') is None:
        notices.append('QA265-NO-FILE-BASED-SOURCE: user brief needs independent reading')

    style=doc.get('narrative_style','NATURAL')
    if style!='NATURAL':
        proof=doc.get('narrative_style_evidence') or {}
        phrase=proof.get('source_quote')
        if not isinstance(phrase,str) or not any(t in phrase.lower() for t in ('布袋戏','布袋戲','puppet','金光','霹雳','霹靂')):
            issues.append('QA265-STYLE-NO-SOURCE-TEXT')
        elif doc.get('narrative_style_source')=='approved_project':
            if source is None or not exact_text(source,phrase):
                issues.append('QA265-STYLE-PROJECT-TAG-NOT-ENOUGH')
        elif doc.get('narrative_style_source')=='user_request':
            notices.append('QA265-STYLE-USER-CLAIM-NEEDS-REVIEW')
        else:
            issues.append('QA265-STYLE-INVALID-ORIGIN')

    for t in doc.get('takes') or []:
        name=t.get('id','?')
        prompt=t.get('prompt')
        if not isinstance(prompt,str):continue
        shot_ids=t.get('shot_ids') or []
        chunks=shot_chunks(prompt) if len(shot_ids)>1 else {}
        for pay in t.get('visible_payoffs') or []:
            if not isinstance(pay,dict):
                issues.append(str(name)+' QA265-PAYOFF-NOT-OBJECT');continue
            sid=pay.get('shot_id')
            quote=pay.get('prompt_quote')
            if not exact_text(prompt,quote):
                issues.append(f'{name} {sid} QA265-PAYOFF-ONLY-IN-MANIFEST')
            if len(shot_ids)>1:
                chunk=chunks.get('SH'+str(sid).upper().replace('-','').replace('_','').removeprefix('SH').zfill(2),[])
                if len(chunk)!=1 or not exact_text(chunk[0],quote):
                    issues.append(f'{name} {sid} QA265-PAYOFF-WRONG-SH')
            if source is not None and not exact_text(source,pay.get('source_quote')):
                issues.append(f'{name} {sid} QA265-PAYOFF-SOURCE-ABSENT')

        if has_speech(prompt):
            proof=t.get('voiceover_evidence') or {}
            if not exact_text(prompt,proof.get('prompt_quote')) or not has_speech(proof.get('prompt_quote')):
                issues.append(f'{name} QA265-UNWITNESSED-VOICE')
            if proof.get('origin')=='script':
                if source is None or not exact_text(source,proof.get('source_quote')) or not has_speech(proof.get('source_quote')):
                    issues.append(f'{name} QA265-NO-SPOKEN-SOURCE')
            elif proof.get('origin')=='user_request':
                if not has_speech(proof.get('source_quote')):
                    issues.append(f'{name} QA265-MISSING-USER-QUOTE')
                else:
                    notices.append(f'{name} QA265-USER-SPEECH-CLAIM-UNVERIFIED')
            else:
                issues.append(f'{name} QA265-BOOLEAN-VOICE-APPROVAL-REJECTED')

        if re.search(r'(?:画面文字|字幕)\s*[：:]',prompt):
            proof=t.get('onscreen_text_evidence') or {}
            if not exact_text(prompt,proof.get('prompt_quote')):
                issues.append(f'{name} QA265-UNWITNESSED-TEXT')
            if source is None or not exact_text(source,proof.get('source_quote')):
                issues.append(f'{name} QA265-TEXT-NOT-IN-SOURCE')

    if doc.get('director_document') is not None:
        expected=[x.get('id') for x in doc.get('editorial_shots') or []]
        anchors=doc.get('director_shots') or []
        if [a.get('shot_id') for a in anchors if isinstance(a,dict)] != expected:
            issues.append('QA265-DIRECTOR-SH-MAP-INCOMPLETE')
        for x in anchors:
            if not isinstance(x,dict):
                issues.append('QA265-DIRECTOR-INVALID-WITNESS');continue
            sid=x.get('shot_id')
            if director is None or not exact_text(director,x.get('director_quote')):
                issues.append(f'{sid} QA265-DIRECTOR-SOURCE-WITNESS-MISSING')
            actual=[t for t in doc.get('takes') or [] if sid in (t.get('shot_ids') or [])]
            if len(actual)!=1 or not exact_text(actual[0].get('prompt'),x.get('prompt_quote')):
                issues.append(f'{sid} QA265-DIRECTOR-NOT-IN-COPY')
    elif doc.get('director_shots'):
        issues.append('QA265-DIRECTOR-SOURCE-DECLARATION-MISSING')
    seen=set()
    for e in doc.get('critical_events') or []:
        if not isinstance(e,dict):
            issues.append('QA265-MALFORMED-EVENT');continue
        eid=e.get('id')
        if not isinstance(eid,str) or not eid.strip() or eid in seen:
            issues.append('QA265-DUPLICATE-EVENT-ID')
        else:seen.add(eid)
        take=[t for t in doc.get('takes') or [] if t.get('id')==e.get('take_id')]
        if len(take)!=1 or not exact_text(take[0].get('prompt'),e.get('prompt_quote')):
            issues.append(f'{eid} QA265-MISSING-COPY-EVENT')
        if source is not None and not exact_text(source,e.get('source_quote')):
            issues.append(f'{eid} QA265-SOURCE-EVENT-CHANGED')
    if source is not None and not doc.get('critical_events'):
        issues.append('QA265-SOURCE-WITHOUT-CRITICAL-EVENT-MAP')
    if not doc.get('critical_events'):
        notices.append('QA265-UNKNOWN-SOURCE-COVERAGE: read user brief manually')

    return {'status':'FAIL' if issues else 'TEXT_STRUCTURE_PASS',
            'errors':list(dict.fromkeys(issues)), 'notices':notices,
            'retained_seconds':b.get('retained_seconds'),
            'scope':'INDEPENDENT STRUCTURAL TRACE; NOT SEMANTIC/ART/CHANNEL/VIDEO QA'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan_json');p.add_argument('--json-out')
    args=p.parse_args()
    data=json.loads(Path(args.plan_json).read_text(encoding='utf-8'))
    for ref in (data.get('source_document'),data.get('director_document')):
        if isinstance(ref,dict) and isinstance(ref.get('path'),str) and ref['path'] and not Path(ref['path']).is_absolute():
            ref['path']=str((Path(args.plan_json).resolve().parent/ref['path']).resolve())
    result=audit(data)
    out=json.dumps(result,ensure_ascii=False,indent=2)
    print(out)
    if args.json_out:Path(args.json_out).write_text(out+'\n',encoding='utf-8')
    return int(result['status']=='FAIL')

if __name__=='__main__':raise SystemExit(main())
