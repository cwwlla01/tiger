#!/usr/bin/env python3
"""Produce reproducible, genuinely anonymized voice cards and a separately-held key.

Not an automated evaluation of distinctive or emotionally persuasive dialogue.
"""
import argparse
import hashlib
import json
import random
import re
from collections import defaultdict, Counter
from pathlib import Path
from audit_script_batch import EP, SPEECH, han


def make_pack(path, min_turns=4, samples=4):
    source = Path(path).read_text(encoding='utf-8')
    eps = list(EP.finditer(source))
    voices = defaultdict(list)
    for i, m in enumerate(eps):
        chunk = source[m.end():eps[i+1].start() if i+1 < len(eps) else len(source)]
        for match in SPEECH.finditer(chunk):
            name = (match.group(1) or match.group(2)).strip()
            line = match.group(3).strip()
            if han(line) >= 8 and not re.fullmatch(r'[\W\s]+', line):
                voices[name].append({'episode': int(m.group(1)), 'line': line})
    eligible = {name: lines for name, lines in voices.items() if len(lines) >= min_turns}
    names = sorted(eligible)
    # A quote naming any candidate discloses a role; repeated quotes create unfairly
    # ambiguous answers, so neither belongs in a role-identification blind set.
    frequency = Counter(item['line'] for rows in eligible.values() for item in rows)
    pool = []
    excluded = {'explicit_name': 0, 'repeated_line': 0}
    for name in names:
        kept = []
        for item in eligible[name]:
            if any(candidate in item['line'] for candidate in names):
                excluded['explicit_name'] += 1
            elif frequency[item['line']] > 1:
                excluded['repeated_line'] += 1
            else:
                kept.append(item)
        pool.append((name, kept))
    rounds = min(samples, min((len(lines) for _, lines in pool), default=0))
    entries = []
    for name, rows in pool:
        for item in rows[:rounds]:
            # Deliberately omit episode from tester cards: role screen-time varies
            # and the episode number can itself identify speakers.
            pool_item = {'role': name, 'line': item['line']}
            pool_item['source_episode'] = item['episode']
            # Collect internally first; never generate IDs before shuffling.
            entries.append(pool_item)
    seed = int.from_bytes(hashlib.sha256(source.encode('utf-8')).digest()[:8], 'big')
    random.Random(seed).shuffle(entries)
    cards = []
    answer = {}
    for i, item in enumerate(entries, 1):
        card_id = f'C{i:03d}'
        cards.append({'id': card_id, 'line': item['line']})
        answer[card_id] = {'role': item['role'], 'source_episode': item['source_episode']}
    return {
        'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'candidate_roles': names,
        'cards': cards,
        'answer_key': answer,
        'excluded': excluded,
        'rounds_per_role': rounds,
        'human_task': 'Give only blind.json to independent readers. They label each card with one candidate role and explain its voice cue. Compare responses to the separately held key; report confusion, accuracy and inter-rater agreement. This pack is not itself a quality test.'
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--output-prefix', required=True)
    a = ap.parse_args()
    data = make_pack(a.file)
    prefix = Path(a.output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    public = {k: v for k, v in data.items() if k != 'answer_key'}
    (prefix.parent / (prefix.name + '_blind.json')).write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding='utf-8')
    (prefix.parent / (prefix.name + '_key.json')).write_text(json.dumps(data['answer_key'], ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'roles': len(data['candidate_roles']), 'cards': len(data['cards']), 'excluded': data['excluded']}, ensure_ascii=False))
