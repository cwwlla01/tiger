"""Conservative structural cross-stage audit for V2.37 emotional tempo contracts."""
import json
import sys
from pathlib import Path

FIELDS = ("beat_id", "tension_intent", "attention_target", "knowledge_mode", "edit_duration_s", "cut_trigger", "sound_role", "protected_hold")
ENUMS = {"tension_intent": {"BUILD", "HOLD", "RELEASE", "SHOCK", "RECOVER"}, "knowledge_mode": {"AUDIENCE_AHEAD", "CHARACTER_AHEAD", "SYNCHRONIZED", "UNCHANGED"}, "sound_role": {"DIEGETIC", "OFFSCREEN", "SILENCE", "MUSIC", "POST_ONLY"}}

def audit(director, compiled):
    if director is None or compiled is None:
        return {"status": "NOT_VERIFIED", "issues": ["MISSING_AUTHORITY_OR_COMPILED"]}
    if not isinstance(director, list) or not isinstance(compiled, list):
        return {"status": "FAIL", "issues": ["INVALID_INPUT_TYPE"]}
    issues=[]
    ids=[x.get("shot_id") for x in director if isinstance(x,dict)]
    if len(ids)!=len(director) or any(not i for i in ids) or len(ids)!=len(set(ids)):
        issues.append("INVALID_DIRECTOR_SHOT_IDS")
    cmap={}
    for x in compiled:
        if not isinstance(x,dict) or not x.get("shot_id"):
            issues.append("INVALID_COMPILED_SHOT_ID");continue
        if x["shot_id"] in cmap:issues.append("DUPLICATE_COMPILED_SHOT")
        cmap[x["shot_id"]]=x
    for shot in director:
        if not isinstance(shot,dict) or not shot.get("shot_id"):continue
        sid=shot["shot_id"]
        for field,values in ENUMS.items():
            if field in shot and shot[field] not in values:issues.append(f"INVALID_{field}:{sid}")
        if shot.get("protected_hold") is True and not shot.get("hold_reason"):
            issues.append(f"UNJUSTIFIED_PROTECTED_HOLD:{sid}")
        if sid not in cmap:issues.append(f"MISSING_SHOT:{sid}");continue
        target=cmap[sid]
        for field in FIELDS:
            if field in shot and target.get(field)!=shot[field]:
                issues.append(f"DRIFT_{field}:{sid}")
    for sid in cmap:
        if sid not in ids:issues.append(f"UNAUTHORIZED_SHOT:{sid}")
    return {"status": "FAIL" if issues else "STRUCTURE_PASS_ONLY", "issues": sorted(set(issues)), "artistic_quality": "NOT_VERIFIED"}

def main():
    if len(sys.argv)!=3:raise SystemExit("Usage: audit_emotional_tempo_v237.py director.json compiled.json")
    d=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    c=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print(json.dumps(audit(d,c),ensure_ascii=False,indent=2))

if __name__=="__main__":main()
