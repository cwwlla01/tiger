#!/usr/bin/env python3
"""Diagnose terse-dialogue repairs without equating line length with dramatic quality."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from audit_adversarial import inspect
from runtime_proxy import estimate


def analyze(path, minimum_average=14):
    if minimum_average <= 0:
        raise ValueError('minimum_average must be positive')
    raw = Path(path).read_bytes()
    structural = inspect(path)['episodes']
    timing = estimate(path)['episodes']
    if len(structural) != 1 or len(timing) != 1 or structural[0]['episode'] != timing[0]['episode']:
        raise ValueError('Expected exactly one matching episode')
    row = timing[0]
    count = row['dialogue_turns']
    current = row['dialogue_han']
    min_chars = math.ceil(count * minimum_average)
    deficit = max(0, min_chars - current)
    # Sensitivity only: no changes are actually made to the source file.
    slow = 180
    fast = 300
    return {
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'episode': row['episode'], 'scenes': row['scenes'], 'dialogue_turns': count,
        'current_dialogue_han': current, 'current_average_han': round(current / max(count, 1), 2),
        'heuristic_average_target_han': minimum_average,
        'chars_to_clear_average_heuristic': deficit,
        'duration_penalty_if_only_adding_chars_seconds': [round(deficit * 60 / fast, 1), round(deficit * 60 / slow, 1)],
        'current_runtime_proxy_seconds': row['estimated_seconds_range'],
        'minimum_proxy_after_pure_addition_seconds': round((current + deficit) * 60 / fast + row['scenes'] * 12),
        'recommendation': ('Do not bulk-extend dialogue. First remove duplicate exposition; only rewrite lines whose choices, rebuttals or consequences are unclear. '
                           'If necessary, redistribute functional dialogue among turns; use scene depth and independent editorial checks. '
                           'The 14-character diagnostic is not an artistic truth.'),
        'status': 'REPAIR_TRADEOFF_REVIEW' if deficit else 'NO_AVERAGE_SHORTFALL',
        'actual_rehearsal_measured': False, 'editorially_approved': False,
    }


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('file'); p.add_argument('--output'); p.add_argument('--minimum-average',type=float,default=14)
    a=p.parse_args()
    result=analyze(a.file,a.minimum_average)
    out=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(out,encoding='utf-8')
    print(out)
