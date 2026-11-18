"""Conservative structured scene-direction handoff audit (V2.21)."""
VALID_FUNCTIONS={"ESTABLISH","DEVELOP","REVEAL","REACTION","PAYOFF","BREATH"}
VALID_DURATIONS={"HOLD","NORMAL","ACCELERATE"}

def audit(data):
    errors=[]
    source=data.get("03") or {}
    for field in ("scene_id","source_anchor","scene_goal","dramatic_question","turning_point","outcome"):
        if not source.get(field):errors.append("03:MISSING:"+field)
    beats=source.get("scene_beats") or []
    shots=source.get("shot_plan") or []
    if not beats:errors.append("03:NO_BEATS")
    if not shots:errors.append("03:NO_SHOTS")
    ids=[s.get("shot_id") for s in shots]
    if len(ids)!=len(set(ids)):errors.append("03:DUPLICATE_SHOT")
    covered=[]
    for shot in shots:
        sid=str(shot.get("shot_id"))
        for field in ("selection_reason","attention_target"):
            if not shot.get(field):errors.append("03:"+sid+":MISSING:"+field)
        if shot.get("function") not in VALID_FUNCTIONS:errors.append("03:"+sid+":BAD_FUNCTION")
        if shot.get("duration_intent") not in VALID_DURATIONS:errors.append("03:"+sid+":BAD_DURATION")
        covered.extend(shot.get("covered_beats") or [])
    for beat in beats:
        if beat not in covered:errors.append("03:UNCOVERED:"+str(beat))
    for beat in covered:
        if beat not in beats:errors.append("03:UNAUTHORIZED_BEAT:"+str(beat))
    for stage in ("04","05"):
        actual=data.get(stage)
        if actual is None:errors.append(stage+":MISSING_STAGE");continue
        if actual.get("scene_id")!=source.get("scene_id"):errors.append(stage+":SCENE_DRIFT")
        got=actual.get("shot_plan") or []
        if [s.get("shot_id") for s in got]!=ids:errors.append(stage+":SHOT_ORDER_DRIFT")
        byid={s.get("shot_id"):s for s in got}
        for shot in shots:
            sid=shot.get("shot_id")
            if sid not in byid:continue
            fields=("covered_beats","function","attention_target")+(("duration_intent",) if stage=="05" else ())
            for field in fields:
                if byid[sid].get(field)!=shot.get(field):errors.append(stage+":"+str(sid)+":DRIFT:"+field)
    return errors
