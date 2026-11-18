#!/usr/bin/env python3
"""Verify episode-to-episode ledger handoff; never certifies untracked story facts."""
import argparse
import hashlib
import json
from pathlib import Path
from audit_continuity_delta import audit


def check_chain(entries):
    problems = []
    results = []
    if not isinstance(entries, list) or len(entries) < 2:
        return {'mechanically_valid':False,'errors':['AT_LEAST_TWO_TRANSITIONS_REQUIRED'], 'narrative_truth_verified':False}
    prior = None
    prior_end = None
    ledger_paths = set()
    transition_pairs = set()
    ledger_fingerprints = set()
    episode_fingerprints = set()
    episode_positions = {}  # hash -> original episode index
    last_changed = {}  # state key -> index of latest documented change/introduction
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or any(k not in entry for k in ('previous_script','current_script','ledger')):
            problems.append(f'INVALID_ENTRY_{i}')
            continue
        try:
            ledger_path = Path(entry['ledger']).resolve()
            if ledger_path in ledger_paths:
                problems.append(f'DUPLICATE_LEDGER_{i}')
            ledger_paths.add(ledger_path)
            pair = (Path(entry['previous_script']).resolve(), Path(entry['current_script']).resolve())
            if pair in transition_pairs:
                problems.append(f'DUPLICATE_TRANSITION_{i}')
            transition_pairs.add(pair)
            ledger_raw = ledger_path.read_bytes()
            ledger_fingerprint = hashlib.sha256(ledger_raw).hexdigest()
            if ledger_fingerprint in ledger_fingerprints:
                problems.append(f'DUPLICATE_LEDGER_CONTENT_{i}')
            ledger_fingerprints.add(ledger_fingerprint)
            ledger = json.loads(ledger_raw.decode('utf-8'))
            report = audit(entry['previous_script'], entry['current_script'], entry['ledger'])
        except (OSError, UnicodeError, ValueError, TypeError) as exc:
            problems.append(f'ENTRY_READ_FAILED_{i}_{type(exc).__name__}')
            continue
        results.append({'transition':i+1,'mechanically_valid':report['mechanically_valid'],'errors':report['errors']})
        if not report['mechanically_valid']:
            problems.append(f'TRANSITION_INVALID_{i}')
        try:
            previous_bytes = Path(entry['previous_script']).read_bytes()
            current_bytes = Path(entry['current_script']).read_bytes()
        except (OSError, ValueError, TypeError) as exc:
            problems.append(f'ENTRY_BYTES_FAILED_{i}_{type(exc).__name__}')
            prior = None
            prior_end = None
            continue
        if previous_bytes == current_bytes:
            problems.append(f'IDENTICAL_EPISODE_BYTES_{i}')
        # A repeated script under a new filename is still the same episode.
        # The previous script is the prior current script for a well-formed chain.
        if i == 0:
            first_hash = hashlib.sha256(previous_bytes).hexdigest()
            episode_fingerprints.add(first_hash)
            episode_positions[first_hash] = 0
        current_fingerprint = hashlib.sha256(current_bytes).hexdigest()
        if current_fingerprint in episode_fingerprints:
            problems.append(f'REPEATED_EPISODE_CONTENT_{i}')
        episode_fingerprints.add(current_fingerprint)
        episode_positions.setdefault(current_fingerprint, i+1)
        # A carried fact must originate from an actual earlier episode in this
        # same manifest, not merely any text file with a matching quote/hash.
        anchors = ledger.get('previous_anchors', {})
        if isinstance(anchors, dict):
            for key, anchor in anchors.items():
                if not isinstance(anchor, dict) or anchor.get('kind') != 'carry_forward':
                    continue
                source_hash = anchor.get('source_sha256')
                source_position = episode_positions.get(source_hash)
                if source_position is None or source_position > i:
                    problems.append(f'CARRY_SOURCE_OUTSIDE_CHAIN_{i}_{key}')
                    continue
                # If the key changed after its quoted source, the quote no
                # longer proves provenance of the current value.
                if last_changed.get(key, -1) > source_position:
                    problems.append(f'CARRY_SOURCE_STALE_AFTER_CHANGE_{i}_{key}')
        for change in ledger.get('changes', []):
            if isinstance(change, dict) and isinstance(change.get('key'), str):
                last_changed[change['key']] = i+1
        for addition in ledger.get('introduced', []):
            if isinstance(addition, dict) and isinstance(addition.get('key'), str):
                last_changed[addition['key']] = i+1
        if prior is not None:
            if prior != previous_bytes:
                problems.append(f'SCRIPT_HANDOFF_MISMATCH_{i}')
            if prior_end != ledger.get('previous_state'):
                problems.append(f'STATE_HANDOFF_MISMATCH_{i}')
        prior = current_bytes
        prior_end = ledger.get('current_state')
    return {'mechanically_valid':not problems,'errors':sorted(set(problems)), 'transitions':results,
            'narrative_truth_verified':False, 'long_series_quality_certified':False,
            'warning':'Checks submitted ledgers and exact file handoff only; cannot detect omitted states or prove narrative meaning.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('manifest',help='JSON list of {previous_script,current_script,ledger}; paths absolute or relative to manifest')
    p.add_argument('--output')
    a=p.parse_args()
    manifest=Path(a.manifest).resolve()
    entries=json.loads(manifest.read_text(encoding='utf-8'))
    for entry in entries if isinstance(entries,list) else []:
        if isinstance(entry,dict):
            for key in ('previous_script','current_script','ledger'):
                if key in entry and not Path(entry[key]).is_absolute():
                    entry[key]=str(manifest.parent / entry[key])
    result=check_chain(entries)
    output=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(output,encoding='utf-8')
    print(output)
    raise SystemExit(0 if result['mechanically_valid'] else 2)

if __name__=='__main__':main()
