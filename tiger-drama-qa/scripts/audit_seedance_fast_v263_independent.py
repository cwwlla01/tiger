#!/usr/bin/env python3
"""Independent V2.63 routing and grouping structure check (not art/video QA)."""
import argparse
import json
from pathlib import Path


def audit(plan):
    faults=[]
    intent=plan.get('intent')
    if intent == 'description':
        if plan.get('delivery_type') != 'description' or plan.get('takes'):
            faults.append('QA-ROUTE: descriptive request improperly became video production')
        if (plan.get('duration_policy') or {}).get('selected_seconds') is not None:
            faults.append('QA-TIME: description cannot inherit fixture duration')
        return {'status':'FAIL' if faults else 'TEXT_STRUCTURE_PASS','errors':faults}
    if intent == 'storyboard':
        if plan.get('delivery_type')!='storyboard': faults.append('QA-ROUTE: storyboard target changed')
        return {'status':'FAIL' if faults else 'TEXT_STRUCTURE_PASS','errors':faults}
    if intent!='seedance_prompt':
        return {'status':'FAIL','errors':['QA-INTENT: unknown input intent']}
    if plan.get('delivery_type')!='seedance_prompt': faults.append('QA-DELIVERY: wrong output format')
    channel=plan.get('channel') or {}
    if channel.get('platform') not in {'jimeng_web','volc_ark_api'}: faults.append('QA-CHANNEL: exact channel absent')
    if channel.get('platform')=='jimeng_web' and channel.get('model_id'): faults.append('QA-CHANNEL-MIX: API ID applied to website')
    if 'fast' not in channel.get('model_display_name','').lower(): faults.append('QA-MODEL: not Fast model')
    if (plan.get('duration_policy') or {}).get('origin')=='fixture_15s' and not plan.get('fixture_id'):
        faults.append('QA-FIXTURE: regression duration leaked to new scene')
    if plan.get('delivery_status')=='SUBMIT_READY' and channel.get('proof_scope') not in {'user_interface_verified','official_exact_channel'}:
        faults.append('QA-CAPABILITY: no same-channel evidence')
    declared=[x.get('id') for x in plan.get('editorial_shots',[])]
    delivered=[]
    for take in plan.get('takes',[]):
        tid=take.get('id','?')
        shots=take.get('shot_ids') or []
        delivered+=shots
        if len(shots)<=1:
            if take.get('grouping')!='SINGLE': faults.append(tid+' QA-GROUP: one SH is not multi-shot')
            continue
        if take.get('grouping')!='MERGE': faults.append(tid+' QA-GROUP: undeclared merge')
        dec=take.get('merge_decision') or {}
        if dec.get('benefit') in {None,'reduce_generation_count','save_cost','supports_multishot'}:
            faults.append(tid+' QA-BENEFIT: no genuine narrative reason')
        if len(dec.get('boundaries') or [])!=len(shots)-1: faults.append(tid+' QA-BOUNDARY: all joins need evidence')
        for idx,b in enumerate(dec.get('boundaries') or []):
            if idx>=len(shots)-1: faults.append(tid+' QA-EXTRA-BOUNDARY');break
            if (b.get('from'),b.get('to'))!=(shots[idx],shots[idx+1]): faults.append(tid+' QA-ORDER: boundary mismatch')
            for key in ('dramatic_reason','continuity_evidence','risk_mitigation'):
                if len((b.get(key) or '').strip())<12: faults.append(tid+' QA-REASON: '+key+' too vague')
            if b.get('risk_level')=='HIGH' and not b.get('pilot_observed'):
                faults.append(tid+' QA-HIGH-RISK: unpiloted contact/complex action must be split')
        if plan.get('delivery_status')=='SUBMIT_READY' and channel.get('multishot_proof')!='same_channel_verified':
            faults.append(tid+' QA-MULTISHOT-PROOF: exact selected channel not demonstrated')
        if len(take.get('shot_timeline') or [])!=len(shots):
            faults.append(tid+' QA-TIME: no per-shot timeline')
    if delivered!=declared: faults.append('QA-COVERAGE: shot omission, duplication or reordering')
    return {'status':'FAIL' if faults else 'TEXT_STRUCTURE_PASS','errors':faults,'evidence':'STRUCTURE_ONLY; NOT_INDEPENDENT_ART_REVIEW'}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('plan_json');a.add_argument('--json-out')
    args=a.parse_args()
    result=audit(json.loads(Path(args.plan_json).read_text(encoding='utf-8')))
    output=json.dumps(result,indent=2,ensure_ascii=False)
    print(output)
    if args.json_out:Path(args.json_out).write_text(output+'\n',encoding='utf-8')
    return int(result['status']=='FAIL')

if __name__=='__main__':raise SystemExit(main())
