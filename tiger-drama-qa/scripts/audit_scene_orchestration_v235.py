"""Conservative structural check for scene-level 03 to 05 handoff. No aesthetic scoring."""
import json
import sys
from pathlib import Path

def audit(data):
    issues=[]
    scene=data.get("scene",{})
    shots=data.get("shots",[])
    compiled=data.get("compiled",[])
    source=set(scene.get("source_beat_ids",[]))
    ids=[s.get("shot_id") for s in shots]
    if len(ids)!=len(set(ids)) or any(not x for x in ids): issues.append("DUPLICATE_OR_EMPTY_SHOT_ID")
    covered={s.get("beat_id") for s in shots}
    if source-covered: issues.append("SOURCE_BEAT_NOT_COVERED")
    if covered-source: issues.append("UNSUPPORTED_BEAT_ID")
    payoff=scene.get("payoff_beat_id")
    if payoff and payoff not in covered: issues.append("PAYOFF_NOT_COVERED")
    if scene.get("audience_knowledge") not in ("AUDIENCE_FIRST","CHARACTER_FIRST","SIMULTANEOUS","UNSPECIFIED"):
        issues.append("UNKNOWN_KNOWLEDGE_MODE")
    shot_map={s.get("shot_id"):s for s in shots}
    compiled_shots=set()
    for c in compiled:
        sid=c.get("shot_id")
        if sid not in shot_map:
            issues.append("UNKNOWN_COMPILED_SHOT"); continue
        compiled_shots.add(sid)
        src=shot_map[sid]
        for field in ("beat_id","camera_choice","cut_trigger","sound_function"):
            if field in src and c.get(field)!=src[field]: issues.append("DRIFT_"+field.upper())
    if set(ids)-compiled_shots: issues.append("SHOT_NOT_COMPILED")
    return {"status":"STRUCTURE_ONLY", "issues":sorted(set(issues)), "shot_count":len(shots), "compiled_count":len(compiled)}

def main():
    if len(sys.argv)!=3:
        print("usage: audit_scene_orchestration_v235.py input.json output.json",file=sys.stderr);return 2
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    Path(sys.argv[2]).write_text(json.dumps(audit(data),ensure_ascii=False,indent=2),encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
