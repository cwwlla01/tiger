#!/usr/bin/env python3
"""Audit time-sampled subject trajectories crossing defined scene light zones.

This is geometric scheduling only, not illumination or video-image validation.
"""
import argparse
import json
import math
from pathlib import Path


def point(p):
    if not isinstance(p, list) or len(p) != 3 or any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) for x in p):
        raise ValueError('point must be finite [x,y,z]')
    return p


def inside(p,z):
    c=point(z['center']); r=z['radius']
    if not isinstance(r,(int,float)) or not math.isfinite(r) or r<=0: raise ValueError('invalid zone radius')
    return math.dist(p,c)<=r


def audit(doc):
    errors=[]; observations=[]
    try:
        zones={z['id']:z for z in doc['zones']}
        if len(zones)!=len(doc['zones']): errors.append('duplicate zone IDs')
        for z in zones.values(): inside([0,0,0],z)
        for take in doc['takes']:
            tid=take['id']; samples=take['samples']
            if len(samples)<2: errors.append(f'{tid}: at least two samples required');continue
            prev=-1
            for s in samples:
                point(s['position']); t=s['time_s']
                if not isinstance(t,(int,float)) or not math.isfinite(t) or t<=prev: raise ValueError(f'{tid}: sample times must increase')
                prev=t
            for z in zones.values():
                membership=[inside(s['position'],z) for s in samples]
                transitions=[]
                for i in range(1,len(samples)):
                    if membership[i]!=membership[i-1]:
                        transitions.append({'between_s':[samples[i-1]['time_s'],samples[i]['time_s']], 'event':'enter' if membership[i] else 'exit'})
                observations.append({'take':tid,'zone':z['id'],'transitions':transitions,'sampled_membership':membership})
                for claim in take.get('zone_claims',[]):
                    if claim['zone_id']!=z['id']:continue
                    if 'start_inside' in claim and claim['start_inside']!=membership[0]: errors.append(f'{tid}: {z["id"]} start membership mismatch')
                    if 'end_inside' in claim and claim['end_inside']!=membership[-1]: errors.append(f'{tid}: {z["id"]} end membership mismatch')
                    if 'transition_count' in claim and claim['transition_count']!=len(transitions): errors.append(f'{tid}: {z["id"]} transition count mismatch')
                    if 'first_transition' in claim and (not transitions or claim['first_transition']!=transitions[0]['event']): errors.append(f'{tid}: {z["id"]} first transition mismatch')
            for claim in take.get('zone_claims',[]):
                if claim['zone_id'] not in zones: errors.append(f'{tid}: unknown zone {claim["zone_id"]}')
    except (KeyError,TypeError,ValueError) as e:
        errors.append(f'invalid input: {e}')
    return {'passed':not errors,'errors':errors,'observations':observations,'scope':'sampled geometry only; no shadow/occlusion/photometry verification'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('manifest');args=parser.parse_args()
    result=audit(json.loads(Path(args.manifest).read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
