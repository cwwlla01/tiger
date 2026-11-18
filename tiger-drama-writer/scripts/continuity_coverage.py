#!/usr/bin/env python3
"""Surface possible continuity facts; require explicit human disposition.

This is a deterministic *candidate coverage* gate, not fact extraction or an
assertion that every story fact was found. A reviewer must read the full script.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

# Broad signals deliberately include false positives, which the editor can dismiss.
PATTERNS = {
    'injury_health': re.compile(r'受伤|骨折|流血|割伤|伤口|住院|昏迷|手术|拐杖|石膏|轮椅'),
    'object_custody': re.compile(r'钥匙|照片|相片|底片|录音|手机|信封|文件|证据|硬盘|病历|监控'),
    'money_obligation': re.compile(r'借款|欠款|赔偿|支付|转账|冻结|三万|债务|收据'),
    'identity_knowledge': re.compile(r'自称|身份|亲眼看见|亲眼见|无法确认|确认|承认|秘密|怀疑|失踪|不可信|证明|名字|姓名'),
    'relationship': re.compile(r'原谅|信任|不信|合作|分手|和解|道歉|背叛'),
}


# High priority requires an explicit event/transfer, not merely a stage direction.
# A passive mention of an object or a glance is still reviewed, but not urgent.
HIGH_RISK = re.compile(r'受伤|骨折|流血|割伤|住院|昏迷|失踪|抢走|交给|交还|递给|归还|移交|给了|转账|赔偿|冻结|更换|签字|确认|换过|偷偷|报警|破损|摔碎|丢失|死亡|被捕')


def build_review_batches(candidates):
    """Presentation only: never merge candidates or allow bulk auto-approval."""
    batches = []
    lookup = {}
    for c in candidates:
        key = (c['scene'], c['priority'])
        if key not in lookup:
            lookup[key] = len(batches)
            batches.append({'scene': c['scene'], 'priority': c['priority'], 'candidate_ids': []})
        batches[lookup[key]]['candidate_ids'].append(c['id'])
    return batches


def scan(script):
    path = Path(script)
    raw = path.read_bytes()
    lines = raw.decode('utf-8').splitlines()
    candidates = []
    scene = ''
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('### SC'):
            scene = stripped
        if not stripped or stripped.startswith('#'):
            continue
        # Only the action/dialogue text, not explanatory prose and section headings.
        if not (stripped.startswith('△') or re.match(r'^[^\s：:]{1,16}[：:]', stripped)):
            continue
        types = sorted(k for k, rx in PATTERNS.items() if rx.search(stripped))
        if not types:
            continue
        cid = hashlib.sha256(f'{number}\0{stripped}'.encode('utf-8')).hexdigest()[:16]
        priority = 'high' if HIGH_RISK.search(stripped) else 'review'
        candidates.append({'id':cid,'line':number,'scene':scene,'categories':types,
                           'priority':priority,'quote':stripped})
    return {'script_sha256':hashlib.sha256(raw).hexdigest(), 'script':str(path),
            'candidates':candidates,
            'review_batches':build_review_batches(candidates),
            'priority_counts':{'high':sum(c['priority']=='high' for c in candidates),
                               'review':sum(c['priority']=='review' for c in candidates)},
            'coverage_is_exhaustive':False,
            'warning':'Priorities and batches are navigation aids only. Every candidate still requires an individual decision; editor must read full script.'}


def audit(scan_result, review, ledger=None):
    errors=[]
    if review.get('script_sha256') != scan_result['script_sha256']:
        errors.append('SCRIPT_HASH_MISMATCH')
    entries=review.get('dispositions')
    if not isinstance(entries,list):
        entries=[];errors.append('DISPOSITIONS_REQUIRED')
    candidate_ids={x['id'] for x in scan_result['candidates']}
    # The optional linkage gate binds editorial decisions to a *real* delta
    # ledger. It proves referenced keys exist, not that their meanings are true.
    current_keys = None
    introduced_keys = set()
    if ledger is not None:
        if ledger.get('current_sha256') != scan_result['script_sha256']:
            errors.append('LEDGER_SCRIPT_HASH_MISMATCH')
        current_state = ledger.get('current_state')
        if not isinstance(current_state,dict):
            errors.append('LEDGER_CURRENT_STATE_REQUIRED')
        else:
            current_keys = set(current_state)
        introduced = ledger.get('introduced')
        if not isinstance(introduced,list):
            errors.append('LEDGER_INTRODUCTIONS_REQUIRED')
        else:
            introduced_keys = {v.get('key') for v in introduced if isinstance(v,dict) and isinstance(v.get('key'),str)}

    seen=set();counts={'track':0,'already_tracked':0,'dismiss':0,'defer':0}
    for idx,item in enumerate(entries):
        if not isinstance(item,dict):
            errors.append(f'INVALID_ENTRY_{idx}');continue
        cid=item.get('id')
        if cid not in candidate_ids:
            errors.append(f'UNKNOWN_CANDIDATE_{idx}');continue
        if cid in seen:
            errors.append(f'DUPLICATE_CANDIDATE_{cid}')
        seen.add(cid)
        decision=item.get('decision')
        if decision not in counts:
            errors.append(f'INVALID_DECISION_{cid}');continue
        counts[decision]+=1
        if len(str(item.get('reason','')).strip())<12:
            errors.append(f'REASON_TOO_SHORT_{cid}')
        if decision in ('track','already_tracked'):
            key=item.get('state_key')
            if not isinstance(key,str) or not key.strip():
                errors.append(f'STATE_KEY_REQUIRED_{cid}')
            elif ledger is not None:
                if current_keys is None or key not in current_keys:
                    errors.append(f'STATE_KEY_NOT_IN_LEDGER_{cid}')
                elif decision == 'track' and key not in introduced_keys:
                    errors.append(f'TRACK_NOT_INTRODUCED_{cid}')

    missing=candidate_ids-seen
    if missing:errors.append(f'UNREVIEWED_CANDIDATES_{len(missing)}')
    if counts['defer']:errors.append(f'DEFERRED_CANDIDATES_{counts["defer"]}')
    if len(str(review.get('editor_full_read_attestation','')).strip())<20:
        errors.append('FULL_READ_ATTESTATION_REQUIRED')
    return {'coverage_review_complete':not errors,'errors':errors,
            'candidate_count':len(candidate_ids),'reviewed_count':len(seen),
            'disposition_counts':counts,'missing_ids':sorted(missing),
            'narrative_truth_verified':False,'all_facts_found':False,
            'warning':'Review coverage is not plot truth or exhaustive continuity validation.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('script');p.add_argument('--review');p.add_argument('--output');p.add_argument('--template');p.add_argument('--ledger',help='Actual continuity delta ledger for state-key linkage')
    args=p.parse_args()
    result=scan(args.script)
    if args.template:
        template={'script_sha256':result['script_sha256'],
                  'editor_full_read_attestation':'',
                  'dispositions':[{'id':c['id'],'decision':'defer','reason':'','state_key':''} for c in result['candidates']]}
        Path(args.template).write_text(json.dumps(template,ensure_ascii=False,indent=2),encoding='utf-8')
    if args.review:
        review=json.loads(Path(args.review).read_text(encoding='utf-8'))
        ledger=json.loads(Path(args.ledger).read_text(encoding='utf-8')) if args.ledger else None
        result['review_audit']=audit(result,review,ledger)
    output=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(output,encoding='utf-8')
    print(output)
    raise SystemExit(2 if args.review and not result['review_audit']['coverage_review_complete'] else 0)

if __name__=='__main__': main()
