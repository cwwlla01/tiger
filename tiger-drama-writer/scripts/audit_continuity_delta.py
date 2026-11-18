#!/usr/bin/env python3
"""Mechanical evidence gate for consecutive episode state transitions.

A ledger documents facts the editor chose to track; this program does not
infer facts, validate interpretation, or certify narrative coherence.
"""
import argparse
import hashlib
import json
from pathlib import Path


def audit(previous_script, current_script, ledger_file):
    previous = Path(previous_script).read_bytes()
    current = Path(current_script).read_bytes()
    prev_text = previous.decode('utf-8')
    curr_text = current.decode('utf-8')
    data = json.loads(Path(ledger_file).read_text(encoding='utf-8'))
    errors = []
    if data.get('previous_sha256') != hashlib.sha256(previous).hexdigest():
        errors.append('PREVIOUS_SHA256_MISMATCH')
    if data.get('current_sha256') != hashlib.sha256(current).hexdigest():
        errors.append('CURRENT_SHA256_MISMATCH')
    prev_state = data.get('previous_state')
    curr_state = data.get('current_state')
    changes = data.get('changes')
    if not isinstance(prev_state, dict) or not isinstance(curr_state, dict):
        return {'mechanically_valid':False,'errors':errors+['STATE_MAP_REQUIRED'], 'narrative_truth_verified':False, 'long_series_quality_certified':False}
    if not isinstance(changes, list):
        return {'mechanically_valid':False,'errors':errors+['CHANGES_LIST_REQUIRED'], 'narrative_truth_verified':False, 'long_series_quality_certified':False}
    # Newly introduced trackable facts are expected in long-running serials.
    # They require an explicit registration and a unique quote from this episode.
    removed = set(prev_state) - set(curr_state)
    if removed:
        errors.extend('DROPPED_TRACKED_KEY_' + key for key in sorted(removed))
    introduced = data.get('introduced', [])
    if not isinstance(introduced, list):
        errors.append('INTRODUCED_LIST_REQUIRED')
        introduced = []
    introduced_seen = set()
    evidence_owners = {}  # Prevent one text span from being reused as independent proof for several state keys.
    def register_evidence(key, quote, item):
        if not isinstance(quote, str) or not quote.strip():
            return
        other = evidence_owners.get(quote)
        if other is not None and other != key:
            reason = item.get('shared_evidence_reason')
            if not isinstance(reason, str) or len(reason.strip()) < 12:
                errors.append(f'CURRENT_EVIDENCE_REUSED_WITHOUT_REASON_{key}')
        else:
            evidence_owners[quote] = key
    for i, item in enumerate(introduced):
        if not isinstance(item, dict):
            errors.append(f'INVALID_INTRODUCTION_{i}'); continue
        key = item.get('key')
        if not isinstance(key, str) or key not in curr_state or key in prev_state:
            errors.append(f'UNKNOWN_INTRODUCTION_{i}'); continue
        if key in introduced_seen:
            errors.append(f'DUPLICATE_INTRODUCTION_{key}')
        introduced_seen.add(key)
        if item.get('value') != curr_state[key]:
            errors.append(f'INTRODUCTION_VALUE_MISMATCH_{key}')
        quote = item.get('current_quote')
        register_evidence(key, quote, item)
        if not isinstance(quote, str) or len(quote.strip()) < 9 or curr_text.count(quote) != 1:
            errors.append(f'INTRODUCTION_QUOTE_NOT_UNIQUE_{key}')
        interpretation = item.get('interpretation')
        if not isinstance(interpretation, str) or len(interpretation.strip()) < 10:
            errors.append(f'INTRODUCTION_MISSING_INTERPRETATION_{key}')
    for key in sorted(set(curr_state) - set(prev_state) - introduced_seen):
        errors.append(f'UNREGISTERED_NEW_KEY_{key}')
    if not prev_state or not curr_state:
        errors.append('EMPTY_STATE_MAP')
    if not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for d in (prev_state,curr_state) for k,v in d.items()):
        errors.append('INVALID_STATE_VALUE')
    seen = set()
    for i, change in enumerate(changes):
        if not isinstance(change,dict):
            errors.append(f'INVALID_CHANGE_{i}'); continue
        key = change.get('key')
        if not isinstance(key,str) or key not in prev_state or key not in curr_state:
            errors.append(f'UNKNOWN_KEY_{i}'); continue
        if key not in prev_state: errors.append(f'CHANGE_NOT_EXISTING_{key}')
        if key in seen: errors.append(f'DUPLICATE_CHANGE_{key}')
        seen.add(key)
        if prev_state[key] == curr_state[key]: errors.append(f'UNCHANGED_LISTED_{key}')
        if change.get('from') != prev_state[key] or change.get('to') != curr_state[key]:
            errors.append(f'CHANGE_VALUES_MISMATCH_{key}')
        quote = change.get('current_quote')
        register_evidence(key, quote, change)
        if not isinstance(quote,str) or len(quote.strip()) < 9 or curr_text.count(quote) != 1:
            errors.append(f'CURRENT_QUOTE_NOT_UNIQUE_{key}')
        interpretation = change.get('interpretation')
        if not isinstance(interpretation,str) or len(interpretation.strip()) < 10:
            errors.append(f'MISSING_INTERPRETATION_{key}')
    for key in sorted(set(prev_state)&set(curr_state)):
        if prev_state[key] != curr_state[key] and key not in seen:
            errors.append(f'UNEXPLAINED_STATE_CHANGE_{key}')
    anchors = data.get('previous_anchors',{})
    if not isinstance(anchors,dict): errors.append('PREVIOUS_ANCHORS_REQUIRED')
    else:
        for extra in sorted(set(anchors) - set(prev_state)):
            errors.append(f'UNEXPECTED_PREVIOUS_ANCHOR_{extra}')
        for key,value in prev_state.items():
            quote=anchors.get(key)
            if isinstance(quote, dict) and quote.get('kind') == 'carry_forward':
                # Not every tracked fact needs to be restated in every episode.
                # This is an explicit editor attestation, NOT a script quote.
                reason = quote.get('review_reason')
                if not isinstance(reason, str) or len(reason.strip()) < 16:
                    errors.append(f'CARRY_FORWARD_REASON_REQUIRED_{key}')
                if quote.get('editor_reviewed') is not True:
                    errors.append(f'CARRY_FORWARD_REVIEW_REQUIRED_{key}')
                # A carry must point to earlier, immutable textual evidence.
                # This proves provenance only, not that no intervening change occurred.
                source_file = quote.get('source_script')
                source_hash = quote.get('source_sha256')
                source_quote = quote.get('source_quote')
                if not isinstance(source_file, str) or not source_file.strip():
                    errors.append(f'CARRY_SOURCE_REQUIRED_{key}')
                else:
                    try:
                        source_path = (Path(ledger_file).resolve().parent / source_file).resolve()
                        source_bytes = source_path.read_bytes()
                        source_text = source_bytes.decode('utf-8')
                    except (OSError, UnicodeError, ValueError):
                        errors.append(f'CARRY_SOURCE_UNREADABLE_{key}')
                    else:
                        if hashlib.sha256(source_bytes).hexdigest() != source_hash:
                            errors.append(f'CARRY_SOURCE_SHA256_MISMATCH_{key}')
                        if (not isinstance(source_quote, str) or len(source_quote.strip()) < 9
                                or source_text.count(source_quote) != 1):
                            errors.append(f'CARRY_SOURCE_QUOTE_NOT_UNIQUE_{key}')
                        if source_bytes == current:
                            errors.append(f'CARRY_SOURCE_IS_CURRENT_EPISODE_{key}')
            elif not isinstance(quote,str) or len(quote.strip()) < 9 or prev_text.count(quote) != 1:
                errors.append(f'PREVIOUS_ANCHOR_NOT_UNIQUE_{key}')
    return {'mechanically_valid':not errors, 'errors':sorted(set(errors)),
            'tracked_keys':len(prev_state), 'documented_changes':len(seen), 'introduced_keys':len(introduced_seen),
            'narrative_truth_verified':False, 'long_series_quality_certified':False,
            'warning':'Provenance and ledger consistency only. Carry-forward annotations are editor attestations, not text evidence; editors must verify facts and missing states.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('previous_script');p.add_argument('current_script');p.add_argument('ledger')
    p.add_argument('--output')
    args=p.parse_args()
    result=audit(args.previous_script,args.current_script,args.ledger)
    body=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(body,encoding='utf-8')
    print(body)
    raise SystemExit(0 if result['mechanically_valid'] else 2)

if __name__=='__main__':main()
