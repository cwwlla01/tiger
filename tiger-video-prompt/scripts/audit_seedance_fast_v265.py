#!/usr/bin/env python3
"""V2.65: source-to-copy-text evidence checks for Seedance Fast candidates.

Adds traceable witnesses to the V2.64 timing/channel checks. A textual witness is
not proof that the artistic interpretation is correct or that a video was made.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from audit_seedance_fast_v264 import audit as audit_v264


SPEECH_MARKER = re.compile(r'(?:旁白|诗号|吟诗)\s*[：:]|\bVOICEOVER\s*:', re.I)
TEXT_MARKER = re.compile(r'(?:画面文字|字幕)\s*[：:]', re.I)


def read_source(ref, errors):
    """Return source text ONLY if file bytes exactly match the declared hash."""
    if not isinstance(ref, dict):
        errors.append('V265-SOURCE-DECLARATION')
        return None
    path = ref.get('path')
    sha = ref.get('sha256')
    if not isinstance(path, str) or not path.strip() or not isinstance(sha, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', sha):
        errors.append('V265-SOURCE-IDENTITY')
        return None
    try:
        file = Path(path)
        if not file.is_file() or file.stat().st_size > 8_000_000:
            raise ValueError('missing or too large')
        content = file.read_bytes()
        if hashlib.sha256(content).hexdigest().lower() != sha.lower():
            errors.append('V265-SOURCE-HASH-DRIFT')
            return None
        return content.decode('utf-8')
    except (OSError, ValueError, UnicodeError):
        errors.append('V265-SOURCE-UNREADABLE')
        return None


def witness(text, quote):
    return isinstance(quote, str) and len(quote.strip()) >= 4 and quote in text


def shot_segment(prompt, shot_ids, shot_id):
    """Give the SH-specific slice for merged prompts, or None if labels unclear."""
    matches = list(re.finditer(r'(?<![\w-])SH[-_]?(\d{1,4})(?!\d)', prompt, re.I))
    if len(matches) < len(shot_ids):
        return None
    target = shot_id.upper().replace('-', '').replace('_', '')
    indices = [i for i, m in enumerate(matches)
               if ('SH' + m.group(1).zfill(2)) == ('SH' + target[2:].zfill(2))]
    if len(indices) != 1:
        return None
    i = indices[0]
    return prompt[matches[i].end(): matches[i+1].start() if i+1 < len(matches) else len(prompt)]


def audit(plan):
    errors = []
    source_ref = plan.get('source_document') if plan.get('intent') == 'seedance_prompt' else None
    source = read_source(source_ref, errors) if source_ref is not None else None
    director_ref = plan.get('director_document') if plan.get('intent') == 'seedance_prompt' else None
    director = read_source(director_ref, errors) if director_ref is not None else None
    # V2.64 had a legacy boolean gate. Supply its compatibility flag ONLY
    # in a private audit copy after verifying V2.65 exact evidence; never
    # promote an ungrounded source_approved_voiceover=True claim.
    compatible = copy.deepcopy(plan)
    for take in compatible.get('takes', []) if plan.get('intent') == 'seedance_prompt' else []:
        prompt = take.get('prompt') or ''
        if not isinstance(prompt, str):
            continue
        v = take.get('voiceover_evidence') or {}
        q = v.get('prompt_quote')
        sq = v.get('source_quote')
        valid_script = (v.get('origin') == 'script' and source is not None
                        and witness(source, sq) and witness(prompt, q)
                        and SPEECH_MARKER.search(sq) and SPEECH_MARKER.search(q))
        valid_user = (v.get('origin') == 'user_request' and isinstance(sq, str)
                      and SPEECH_MARKER.search(sq) and witness(prompt, q)
                      and SPEECH_MARKER.search(q))
        if valid_script or valid_user:
            take['source_approved_voiceover'] = True
        t = take.get('onscreen_text_evidence') or {}
        if source is not None and witness(source, t.get('source_quote')) and witness(prompt, t.get('prompt_quote')):
            take['source_approved_onscreen_text'] = True
    base = audit_v264(compatible)
    errors.extend(base.get('errors', []))
    notices = list(base.get('notices', []))
    if plan.get('intent') != 'seedance_prompt':
        return {'status':'FAIL' if errors else 'TEXT_STRUCTURE_PASS', 'errors':errors,
                'notices':notices, 'scope':'ROUTING_ONLY; NO VIDEO PRODUCED'}
    if source_ref is None:
        notices.append('V265-SOURCE-NOT-FILE-VERIFIED: direct chat briefs still require human fact review')

    style = plan.get('narrative_style', 'NATURAL')
    if style != 'NATURAL':
        evidence = plan.get('narrative_style_evidence') or {}
        quote = evidence.get('source_quote')
        origin = plan.get('narrative_style_source')
        if not isinstance(quote, str) or not any(x in quote.lower() for x in ('布袋戏','布袋戲','puppet','金光','霹雳','霹靂')):
            errors.append('V265-STYLE-EVIDENCE: style needs explicit meaningful source text')
        elif origin == 'approved_project':
            if source is None or not witness(source, quote):
                errors.append('V265-STYLE-PROVENANCE: approved_project cannot be a free-standing tag')
        elif origin == 'user_request':
            notices.append('V265-STYLE-USER-QUOTE: user-message evidence needs human confirmation')
        else:
            errors.append('V265-STYLE-ORIGIN')

    for take in plan.get('takes', []):
        tid = take.get('id', '?')
        prompt = take.get('prompt')
        if not isinstance(prompt, str):
            continue
        ids = take.get('shot_ids') or []
        payoff = take.get('visible_payoffs') or []
        for p in payoff:
            if not isinstance(p, dict):
                errors.append(f'{tid} V265-PAYOFF-MALFORMED')
                continue
            sid = p.get('shot_id', '?')
            quote = p.get('prompt_quote')
            if not witness(prompt, quote):
                errors.append(f'{tid} {sid} V265-PAYOFF-NOT-IN-COPY: metadata is not a prompt witness')
            if len(ids) > 1:
                slice_ = shot_segment(prompt, ids, sid)
                if slice_ is None or not witness(slice_, quote):
                    errors.append(f'{tid} {sid} V265-PAYOFF-WRONG-SHOT: witness must be in this editorial SH')
            if source is not None and not witness(source, p.get('source_quote')):
                errors.append(f'{tid} {sid} V265-PAYOFF-SOURCE: no exact source quote')

        if SPEECH_MARKER.search(prompt):
            evidence = take.get('voiceover_evidence') or {}
            source_quote = evidence.get('source_quote')
            prompt_quote = evidence.get('prompt_quote')
            if not witness(prompt, prompt_quote) or not SPEECH_MARKER.search(prompt_quote or ''):
                errors.append(f'{tid} V265-VOICE-WITNESS: actual prompt narration must be identified')
            if evidence.get('origin') == 'script':
                if source is None or not witness(source, source_quote) or not SPEECH_MARKER.search(source_quote or ''):
                    errors.append(f'{tid} V265-VOICE-SOURCE: no script-backed spoken narration')
            elif evidence.get('origin') == 'user_request':
                if not isinstance(source_quote, str) or not SPEECH_MARKER.search(source_quote):
                    errors.append(f'{tid} V265-VOICE-USER-QUOTE')
                else:
                    notices.append(f'{tid} V265-VOICE-CHAT-UNVERIFIED: review actual user wording')
            else:
                errors.append(f'{tid} V265-VOICE-ORIGIN: a boolean approval is not evidence')

        if TEXT_MARKER.search(prompt):
            evidence = take.get('onscreen_text_evidence') or {}
            if not witness(prompt, evidence.get('prompt_quote')):
                errors.append(f'{tid} V265-TEXT-WITNESS')
            if source is None or not witness(source, evidence.get('source_quote')):
                errors.append(f'{tid} V265-TEXT-SOURCE: exact lettering needs a real source')

    if director_ref is not None:
        declared = [s.get('id') for s in plan.get('editorial_shots') or []]
        lines = plan.get('director_shots') or []
        if [s.get('shot_id') for s in lines if isinstance(s, dict)] != declared:
            errors.append('V265-DIRECTOR-SHOT-COVERAGE: each director SH needs a source witness')
        for item in lines:
            if not isinstance(item, dict):
                errors.append('V265-DIRECTOR-SHOT-MALFORMED');continue
            sh=item.get('shot_id')
            if director is None or not witness(director,item.get('director_quote')):
                errors.append(f'{sh} V265-DIRECTOR-SOURCE: SH has no real director excerpt')
            takelist=[t for t in plan.get('takes',[]) if sh in (t.get('shot_ids') or [])]
            if len(takelist)!=1 or not witness(takelist[0].get('prompt',''),item.get('prompt_quote')):
                errors.append(f'{sh} V265-DIRECTOR-PROMPT: director shot not grounded in copy text')
    elif plan.get('director_shots'):
        errors.append('V265-DIRECTOR-DOCUMENT-MISSING: orphaned director witnesses')
    event_ids=set()
    for e in plan.get('critical_events') or []:
        if not isinstance(e, dict):
            errors.append('V265-EVENT-MALFORMED');continue
        name = e.get('id')
        tid = e.get('take_id')
        matching = [t for t in plan.get('takes', []) if t.get('id')==tid]
        if not isinstance(name,str) or not name.strip() or name in event_ids:
            errors.append('V265-EVENT-ID')
        else:
            event_ids.add(name)
        if len(matching)!=1 or not witness(matching[0].get('prompt',''),e.get('prompt_quote')):
            errors.append(f'{name} V265-EVENT-PROMPT: required event has no exact prompt witness')
        if source is not None and not witness(source,e.get('source_quote')):
            errors.append(f'{name} V265-EVENT-SOURCE: required event is not tied to source')
    if source is not None and not plan.get('critical_events'):
        errors.append('V265-EVENT-COVERAGE: source-backed plans need an explicit critical-event list')
    if not plan.get('critical_events'):
        notices.append('V265-FACT-REVIEW: script cannot infer all user requirements; compare source manually')

    return {'status':'FAIL' if errors else 'TEXT_STRUCTURE_PASS',
            'errors':list(dict.fromkeys(errors)), 'notices':list(dict.fromkeys(notices)),
            'edit_total_seconds':base.get('edit_total_seconds'),
            'scope':'SOURCE_HASH_AND_EXACT_TEXT_WITNESSES_ONLY; SEMANTIC_REVIEW_AND_VIDEO_NOT_VERIFIED'}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('plan_json')
    a.add_argument('--json-out')
    args=a.parse_args()
    data=json.loads(Path(args.plan_json).read_text(encoding='utf-8'))
    for ref in (data.get('source_document'),data.get('director_document')):
        if isinstance(ref,dict) and isinstance(ref.get('path'),str) and ref['path'] and not Path(ref['path']).is_absolute():
            ref['path']=str((Path(args.plan_json).resolve().parent/ref['path']).resolve())
    out=audit(data)
    s=json.dumps(out,indent=2,ensure_ascii=False)
    print(s)
    if args.json_out:Path(args.json_out).write_text(s+'\n',encoding='utf-8')
    return int(out['status']=='FAIL')


if __name__=='__main__':raise SystemExit(main())
