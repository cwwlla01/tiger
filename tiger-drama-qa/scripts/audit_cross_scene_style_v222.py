"""V2.22 conservative structured cross-scene style handoff audit."""
VALID_MODES={"BASELINE","JUSTIFIED_DEVIATION"}
FIELDS=("bible_id","bible_version","style_mode","style_intent","attention_rule","motif_ids")
def audit(data):
    errors=[]
    bible=data.get("style_bible") or {}
    for field in ("bible_id","bible_version","authority_anchor","project_id"):
        if not bible.get(field):errors.append("BIBLE:MISSING:"+field)
    approved=set(bible.get("motif_registry") or [])
    source=data.get("03") or []
    ids=[s.get("scene_id") for s in source]
    if not source:errors.append("03:NO_SCENES")
    if len(ids)!=len(set(ids)):errors.append("03:DUPLICATE_SCENE")
    for s in source:
        sid=str(s.get("scene_id"))
        for field in ("scene_id","source_anchor","style_intent","attention_rule","rhythm_rule"):
            if not s.get(field):errors.append("03:"+sid+":MISSING:"+field)
        for field in ("bible_id","bible_version"):
            if s.get(field)!=bible.get(field):errors.append("03:"+sid+":BIBLE_DRIFT:"+field)
        if s.get("style_mode") not in VALID_MODES:errors.append("03:"+sid+":BAD_MODE")
        if s.get("style_mode")=="JUSTIFIED_DEVIATION" and not s.get("style_exception_reason"):
            errors.append("03:"+sid+":UNJUSTIFIED_DEVIATION")
        for motif in s.get("motif_ids") or []:
            if motif not in approved:errors.append("03:"+sid+":UNAPPROVED_MOTIF:"+str(motif))
    for stage in ("04","05"):
        actual=data.get(stage)
        if actual is None:errors.append(stage+":MISSING_STAGE");continue
        if [s.get("scene_id") for s in actual]!=ids:errors.append(stage+":SCENE_ORDER_DRIFT")
        byid={s.get("scene_id"):s for s in actual}
        for s in source:
            sid=s.get("scene_id")
            if sid not in byid:continue
            fields=FIELDS+(("rhythm_rule",) if stage=="05" else ())
            for field in fields:
                if byid[sid].get(field)!=s.get(field):errors.append(stage+":"+str(sid)+":DRIFT:"+field)
    return errors
