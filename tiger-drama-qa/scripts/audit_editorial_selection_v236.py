"""Conservative structural audit of editorial selection records; no artistic scoring."""
import json
import sys
from pathlib import Path

PROTECTED = {"SUSPENSE_HOLD", "REACTION", "SPATIAL_ORIENTATION", "SOUND_BRIDGE"}
DECISIONS = {"KEEP", "MERGE", "TRIM", "REMOVE", "ESCALATE"}

def audit(data):
    issues=[]
    shots=data.get("shots", [])
    if not isinstance(shots,list): return ["INVALID_SHOTS"]
    ids=[s.get("shot_id") for s in shots if isinstance(s,dict)]
    if len(ids)!=len(set(ids)) or any(not x for x in ids): issues.append("SHOT_ID_INVALID")
    preserved=set()
    for s in shots:
        if not isinstance(s,dict): issues.append("INVALID_SHOT"); continue
        decision=s.get("decision")
        if decision not in DECISIONS: issues.append("INVALID_DECISION"); continue
        beats=s.get("source_beat_ids")
        if not isinstance(beats,list) or not beats or any(not isinstance(x,str) or not x for x in beats): issues.append("MISSING_BEAT_LINK"); continue
        if not s.get("reason") or not s.get("dramatic_function"): issues.append("MISSING_RATIONALE")
        if decision in ("KEEP","MERGE","TRIM"): preserved.update(beats)
        if decision=="REMOVE" and s.get("dramatic_function") in PROTECTED and not s.get("protected_override_evidence"): issues.append("PROTECTED_SHOT_REMOVED")
        if decision=="REMOVE" and not s.get("replacement_shot_ids"): issues.append("REMOVAL_WITHOUT_REPLACEMENT")
        if decision=="ESCALATE": issues.append("UNRESOLVED_ESCALATION")
    expected=data.get("required_source_beats")
    if not isinstance(expected,list) or not expected: issues.append("MISSING_SOURCE_BASELINE")
    else:
        if set(expected)-preserved: issues.append("SOURCE_BEAT_LOST")
    for s in shots:
        if isinstance(s,dict) and s.get("decision")=="REMOVE":
            repl=s.get("replacement_shot_ids",[])
            if not isinstance(repl,list) or any(x not in ids or x==s.get("shot_id") for x in repl): issues.append("INVALID_REPLACEMENT")
    return sorted(set(issues))

def main():
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    issues=audit(data)
    print(json.dumps({"status":"PASS" if not issues else "FAIL","issues":issues},ensure_ascii=False))
    return int(bool(issues))

if __name__=="__main__": raise SystemExit(main())
