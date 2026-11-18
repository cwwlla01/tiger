#!/usr/bin/env python3
"""Evidence-bound, per-episode *review record*. Does not objectively grade dramatic quality.

Requires operator-authored citations for four independent categories and binds them
cryptographically to the exact episode bytes. Static gate must pass separately.
"""
import argparse, hashlib, json
from pathlib import Path
from episode_stop_gate import check

CATEGORIES=('action_counteraction','irreversible_change','genre_payoff_or_debt','continuity_delta')

def authorize(episode_path, episode_no, review_path):
    source=Path(episode_path)
    raw=source.read_bytes()
    text=raw.decode('utf-8')
    review=json.loads(Path(review_path).read_text(encoding='utf-8'))
    gate=check(source,episode_no)
    problems=list(gate['issues'])
    if not gate['static_ready_for_editorial_review']:
        problems.append('STATIC_GATE_NOT_PASSED')
    digest=hashlib.sha256(raw).hexdigest()
    if review.get('episode')!=episode_no:problems.append('REVIEW_EPISODE_MISMATCH')
    if review.get('sha256')!=digest:problems.append('SOURCE_HASH_MISMATCH')
    if review.get('reviewer') in (None,'','automated','auto'):problems.append('REVIEWER_NOT_RECORDED')
    evidence=review.get('evidence',{})
    for category in CATEGORIES:
        item=evidence.get(category)
        if not isinstance(item,dict) or not item.get('assessment') or not item.get('quote'):
            problems.append('MISSING_'+category.upper());continue
        quote=item['quote'].strip()
        if len(quote)<8 or quote not in text:
            problems.append('UNSUPPORTED_'+category.upper())
    if review.get('editorial_decision')!='approved':problems.append('EDITORIAL_NOT_APPROVED')
    return {'episode':episode_no,'sha256':digest,'static_ready':gate['static_ready_for_editorial_review'],
            'review_record_valid':not problems,'next_episode_authorized':not problems,
            'issues':sorted(set(problems)),
            'caveat':'Only verifies that a named review record cites the exact unmodified script; no independent artistic/timing validation.'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('episode_file');a.add_argument('review_json');a.add_argument('--episode',type=int,required=True);a.add_argument('--output');args=a.parse_args()
    result=authorize(args.episode_file,args.episode,args.review_json)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(payload,encoding='utf-8')
    print(payload)
    raise SystemExit(0 if result['next_episode_authorized'] else 2)
