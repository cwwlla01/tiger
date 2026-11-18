"""V2.11 production handoff gate. Structural evidence checks, not artistic QA."""
import argparse
import json
from pathlib import Path

STAGES = ('03', '04', '05')

def audit(data):
    issues = []
    takes = data.get('takes', [])
    seen = set()
    for i, take in enumerate(takes):
        tid = take.get('take_id', f'index:{i}')
        if tid in seen:
            issues.append({'code':'DUPLICATE_TAKE','take_id':tid,'severity':'P0'})
        seen.add(tid)
        evidence = take.get('evidence', {})
        stage = take.get('stage', '03')
        if stage not in STAGES:
            issues.append({'code':'UNKNOWN_STAGE','take_id':tid,'severity':'P1'})
        if take.get('canonical_conflict'):
            issues.append({'code':'CANON_CONFLICT','take_id':tid,'severity':'P0'})
        if take.get('geometry_uncertain') and not take.get('fallback_shot'):
            issues.append({'code':'MISSING_FALLBACK','take_id':tid,'severity':'P1'})
        if take.get('simulation_rounds', 0) > 2 and not take.get('new_authoritative_evidence'):
            issues.append({'code':'SIMULATION_LOOP','take_id':tid,'severity':'P1'})
        if stage in ('04','05'):
            if not data.get('director_frozen', False) and take.get('delivery_status') == 'FORMAL':
                issues.append({'code':'UNFROZEN_FORMAL','take_id':tid,'severity':'P0'})
            if take.get('director_hash') != data.get('director_hash') or not take.get('director_hash'):
                issues.append({'code':'DIRECTOR_VERSION_MISMATCH','take_id':tid,'severity':'P0'})
            if take.get('unapproved_director_change'):
                issues.append({'code':'UNAPPROVED_REDIRECT','take_id':tid,'severity':'P0'})
        if take.get('claims_video_qa_passed') and not evidence.get('video_review'):
            issues.append({'code':'UNSUPPORTED_VIDEO_PASS','take_id':tid,'severity':'P0'})
        if take.get('claims_asset_verified') and not evidence.get('asset_verified'):
            issues.append({'code':'UNSUPPORTED_ASSET_PASS','take_id':tid,'severity':'P0'})
        if take.get('claims_physics_verified') and evidence.get('physics') in (None, 'simulation'):
            issues.append({'code':'SIMULATION_OVERCLAIM','take_id':tid,'severity':'P1'})
    return {'pass': not issues, 'issues':issues, 'take_count':len(takes)}

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('input')
    a=p.parse_args()
    result=audit(json.loads(Path(a.input).read_text(encoding='utf-8')))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['pass'] else 1)
