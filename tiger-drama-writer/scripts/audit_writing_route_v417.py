#!/usr/bin/env python3
"""V4.17 deterministic DELIVERY ROUTE preflight. Not an AI literary evaluator."""
import argparse
import json
from pathlib import Path

MODES={'NATURAL','PUPPET_STRUCTURAL','PUPPET_MODERATE','PUPPET_FULL_REQUESTED'}
ARTIFACTS={'screenplay','outline','evaluation','description'}

def audit(plan):
    errors=[]
    asked=plan.get('user_artifact')
    given=plan.get('delivered_artifact')
    if asked not in ARTIFACTS or given!=asked: errors.append('ROUTE: respect user-requested artifact')
    if asked=='screenplay':
        if not plan.get('full_playable_text'): errors.append('DELIVERY: no complete screenplay')
        if not plan.get('stageable_actions_and_dialogue'): errors.append('DELIVERY: not playable')
        if plan.get('outline_before_script') and not plan.get('outline_requested'):
            errors.append('DELIVERY: unsolicited planning outline before completed screenplay')
    if asked in ('description','evaluation','outline') and plan.get('auto_converted_to_script'):
        errors.append('SCOPE: extra script not authorised')
    style=plan.get('style','NATURAL')
    if style not in MODES: errors.append('STYLE: unknown profile')
    if style!='NATURAL' and not(plan.get('style_requested') or plan.get('approved_project_style')):
        errors.append('STYLE: stylization not approved')
    if style!='PUPPET_FULL_REQUESTED' and plan.get('compulsory_poetry'):
        errors.append('STYLE: unrequested mandatory 诗号')
    if plan.get('unsourced_voiceover'):
        errors.append('SOURCE: newly inserted unsourced narration')
    return {'status':'FAIL' if errors else 'TEXT_ROUTE_PASS','errors':errors,
            'scope':'PLAN CLAIMS ONLY; NOT SCREENPLAY CONTENT OR AUDIENCE QA'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest_json')
    a=p.parse_args();result=audit(json.loads(Path(a.manifest_json).read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return int(result['status']=='FAIL')

if __name__=='__main__':raise SystemExit(main())
