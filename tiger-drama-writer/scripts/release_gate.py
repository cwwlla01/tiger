#!/usr/bin/env python3
"""Conservative batch readiness gate; does not establish artistic quality or runtime."""
import argparse, json
from pathlib import Path
from audit_script_batch import audit
from audit_adversarial import inspect
from audit_scene_depth import audit as scene_audit
from check_serial_decay import assess as decay_assess

def evaluate(files):
    results=[]
    for f in files:
        st=audit(f); adv=inspect(f); depth=scene_audit(f); decay=decay_assess(f)
        issues=[]
        if st.get('error'): issues.append('PARSER_FAILURE')
        if st.get('duplicates'): issues.append('DUPLICATE_EPISODES')
        if st.get('missing_between_minmax'): issues.append('MISSING_EPISODES')
        for ep in st.get('episodes',[]):
            n=ep['episode']
            if ep['status'] != 'STRUCTURALLY_REVIEWABLE': issues.append(f'EP{n:02d}_STRUCTURE_REVIEW')
        for ep in adv.get('episodes',[]):
            n=ep['episode']
            for flag in ep['adversarial_flags']:
                if flag=='UNWRITTEN_PLACEHOLDER_BLOCKER': issues.append(f'EP{n:02d}_UNWRITTEN_BLOCKER')
                else: issues.append(f'EP{n:02d}_{flag}')
        for ep in depth.get('episodes', []):
            n=ep['episode']
            for idx, scene in enumerate(ep['scenes'], 1):
                for flag in scene['flags']:
                    issues.append(f'EP{n:02d}_SCENE{idx:02d}_{flag}')
        for flag in decay.get('issues', []):
            issues.append(f'SERIAL_{flag}')
        results.append({'file':str(f),'episodes':len(st.get('episodes',[])),'issues':sorted(set(issues)),'screening_ready':not issues})
    return {'batch_screening_ready': bool(results) and all(r['screening_ready'] for r in results),'files':results,'required_human_gates':['causality_and_character','payoff_and_genre','cross_episode_continuity','read_through_timing'],'note':'Screening ready is never an artistic, production or timed-runtime certificate.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('files',nargs='+');p.add_argument('--output');a=p.parse_args()
    obj=evaluate(a.files);s=json.dumps(obj,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(s,encoding='utf-8')
    print(s)
