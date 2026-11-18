#!/usr/bin/env python3
"""Verify ordered, episode-local evidence for an emotional choice and consequence.

This checks provenance and chronology, not artistic quality or sincerity.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

FIELDS = ('pressure', 'costly_choice', 'visible_cost', 'relationship_shift')
SCENE = re.compile(r'^###\s+SC\d+[^\n]*', re.M)


def audit(script_path, ledger_path):
    data = Path(script_path).read_bytes()
    script = data.decode('utf-8')
    ledger = json.loads(Path(ledger_path).read_text(encoding='utf-8'))
    errors = []
    if ledger.get('script_sha256') != hashlib.sha256(data).hexdigest():
        errors.append('SCRIPT_SHA256_MISMATCH')
    scenes = list(SCENE.finditer(script))
    if not scenes:
        errors.append('NO_SCENES')
    points = []
    for field in FIELDS:
        record = ledger.get('evidence', {}).get(field)
        if not isinstance(record, dict):
            errors.append(f'MISSING_{field.upper()}')
            continue
        quote = record.get('quote')
        rationale = record.get('interpretation')
        if not isinstance(quote, str) or len(quote.strip()) < 9:
            errors.append(f'SHORT_QUOTE_{field.upper()}')
            continue
        if not isinstance(rationale, str) or len(rationale.strip()) < 12:
            errors.append(f'MISSING_INTERPRETATION_{field.upper()}')
        locations = [m.start() for m in re.finditer(re.escape(quote), script)]
        if len(locations) != 1:
            errors.append(f'QUOTE_NOT_UNIQUE_{field.upper()}')
            continue
        pos = locations[0]
        scene_index = next((i+1 for i,m in enumerate(scenes) if m.end() <= pos and (i+1 == len(scenes) or scenes[i+1].start() > pos)), None)
        if scene_index is None:
            errors.append(f'QUOTE_OUTSIDE_SCENE_{field.upper()}')
            continue
        if record.get('scene') != scene_index:
            errors.append(f'SCENE_MISMATCH_{field.upper()}')
        points.append((field,pos,scene_index))
    if len(points) == 4 and [x[1] for x in points] != sorted(x[1] for x in points):
        errors.append('NONCHRONOLOGICAL_ARC')
    roles = ledger.get('character')
    if not isinstance(roles,str) or not roles.strip():
        errors.append('MISSING_CHARACTER')
    return {'accepted_for_human_review': not errors, 'artistic_quality_certified': False, 'errors':errors, 'scene_count':len(scenes), 'anchors': [{'beat': k,'scene': sc} for k,_,sc in points]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('script');p.add_argument('ledger');p.add_argument('--output')
    a=p.parse_args()
    result=audit(a.script,a.ledger)
    if a.output: Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['accepted_for_human_review'] else 2

if __name__=='__main__': raise SystemExit(main())
