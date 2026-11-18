#!/usr/bin/env python3
"""Audit fixed world-space light anchors and per-take screen-side claims."""
import argparse
import json
import math
from pathlib import Path


def vec(x):
    if not isinstance(x, list) or len(x) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in x):
        raise ValueError('expected finite [x,y,z] vector')
    return x


def sub(a,b): return [a[i]-b[i] for i in range(3)]
def dot(a,b): return sum(a[i]*b[i] for i in range(3))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def norm(a):
    d=math.sqrt(dot(a,a))
    if d < 1e-8: raise ValueError('degenerate camera direction or up vector')
    return [v/d for v in a]


def audit(doc):
    errors=[]; results=[]
    try:
        anchors={x['id']:vec(x['position']) for x in doc['lights']}
        if len(anchors)!=len(doc['lights']): errors.append('duplicate light ID')
        for take in doc['takes']:
            tid=take['id']; camera=take['camera']; position=vec(camera['position']); target=vec(camera['target']); up=vec(camera.get('up',[0,0,1])); subject=vec(take['subject_position'])
            right=norm(cross(norm(sub(target,position)),up))
            for claim in take['light_claims']:
                lid=claim['light_id']
                if lid not in anchors:
                    errors.append(f'{tid}: unknown light {lid}');continue
                if 'world_position' in claim and any(abs(a-b)>1e-5 for a,b in zip(vec(claim['world_position']),anchors[lid])):
                    errors.append(f'{tid}: {lid} world position changed')
                lateral=dot(sub(anchors[lid],subject),right)
                actual='center' if abs(lateral)<0.05 else ('right' if lateral>0 else 'left')
                expected=claim.get('screen_side')
                if expected and expected!=actual: errors.append(f'{tid}: {lid} screen side expected {expected}, computed {actual}')
                results.append({'take':tid,'light':lid,'computed_screen_side':actual,'lateral_offset':round(lateral,4)})
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f'invalid input: {exc}')
    return {'passed':not errors,'errors':errors,'observations':results}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');a=p.parse_args()
    result=audit(json.loads(Path(a.manifest).read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
