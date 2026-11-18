#!/usr/bin/env python3
"""Simplified geometric face-light visibility checks; not a renderer."""
import argparse, json, math
from pathlib import Path

def v(a):
    if not isinstance(a,list) or len(a)!=3 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in a): raise ValueError('expected finite 3D vector')
    return a

def sub(a,b): return [a[i]-b[i] for i in range(3)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a):
    n=math.sqrt(dot(a,a))
    if n<1e-9: raise ValueError('zero-length vector')
    return [x/n for x in a]

def blocked(a,b,obstacles):
    # Segment versus axis-aligned box; only explicit opaque boxes.
    d=sub(b,a)
    for box in obstacles:
        lo=v(box['min']); hi=v(box['max'])
        if any(lo[i]>hi[i] for i in range(3)): raise ValueError('invalid obstacle bounds')
        if box.get('opaque',True) is False: continue
        near=0.; far=1.
        for i in range(3):
            if abs(d[i])<1e-10:
                if a[i]<lo[i] or a[i]>hi[i]: far=-1.;break
            else:
                t1=(lo[i]-a[i])/d[i];t2=(hi[i]-a[i])/d[i]
                near=max(near,min(t1,t2));far=min(far,max(t1,t2))
        if near<=far and far>1e-6 and near<1-1e-6: return True
    return False

def audit(doc):
    errors=[]; obs=[]
    try:
        lights={l['id']:l for l in doc['lights']}
        if len(lights)!=len(doc['lights']): errors.append('duplicate light IDs')
        obstacles=doc.get('obstacles',[])
        for take in doc['takes']:
            tid=take['id']; samples=take['samples']; prev=-float('inf')
            if not samples: errors.append(f'{tid}: no samples');continue
            for s in samples:
                t=s['time_s']
                if isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t) or t<=prev: raise ValueError(f'{tid}: invalid sample times')
                prev=t; face=v(s['face_position']); facing=norm(v(s['face_forward']))
                for claim in s['light_claims']:
                    lid=claim['light_id']
                    if lid not in lights: errors.append(f'{tid}: unknown light {lid}');continue
                    light=lights[lid]; pos=v(light['position']); ray=norm(sub(pos,face))
                    incidence=dot(facing,ray)
                    threshold=light.get('face_incidence_threshold',0.15)
                    if not isinstance(threshold,(int,float)) or not -1<=threshold<=1: raise ValueError('invalid threshold')
                    obstruction=blocked(face,pos,obstacles)
                    status='occluded' if obstruction else ('front_lit' if incidence>threshold else 'not_front_lit')
                    obs.append({'take':tid,'time_s':t,'light':lid,'face_status':status,'incidence':round(incidence,4),'occluded':obstruction})
                    if claim.get('expected_face_status') and claim['expected_face_status']!=status:
                        errors.append(f'{tid}@{t}: {lid} face status expected {claim["expected_face_status"]}, computed {status}')
    except (KeyError,ValueError,TypeError) as e: errors.append(f'invalid input: {e}')
    return {'passed':not errors,'errors':errors,'observations':obs,'scope':'geometric front-face incidence and AABB occlusion only; no photometry, bounce light, shadows, or video verification'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest');a=p.parse_args()
    result=audit(json.loads(Path(a.manifest).read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result['passed'] else 1)
