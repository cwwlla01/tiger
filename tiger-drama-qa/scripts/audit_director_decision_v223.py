"""Conservative V2.23 structured decision handoff audit."""
REQUIRED=("decision_id","selected_candidate_id","source_anchors","scene_goal","beat_coverage","style_version")

def audit(data):
    errors=[]
    d=data.get("03")
    if not isinstance(d,dict):return ["MISSING_03"]
    candidates=d.get("candidates",[])
    if not isinstance(candidates,list):return ["BAD_CANDIDATES"]
    ids=[c.get("candidate_id") for c in candidates if isinstance(c,dict)]
    if len(ids)!=len(set(ids)) or any(not x for x in ids):errors.append("DUPLICATE_OR_EMPTY_CANDIDATE")
    selected=d.get("selected_candidate_id")
    if selected not in ids:errors.append("SELECTED_NOT_FOUND")
    else:
        c=next(c for c in candidates if c.get("candidate_id")==selected)
        if not c.get("hard_gate_pass",False) or c.get("veto_reasons"):errors.append("VETOED_SELECTED")
        if c.get("ai_feasibility")=="UNSUPPORTED":errors.append("UNSUPPORTED_SELECTED")
        if c.get("ai_feasibility")=="PILOT_REQUIRED" and d.get("model_verified") is True:errors.append("PILOT_MISREPRESENTED")
    if d.get("status")=="BLOCKED_REVISE" and selected:errors.append("BLOCKED_WITH_SELECTION")
    for field in REQUIRED:
        if d.get(field) in (None,"",[]):errors.append("MISSING_03_"+field.upper())
    for stage in ("04","05"):
        item=data.get(stage)
        if not isinstance(item,dict):errors.append("MISSING_"+stage);continue
        for field in REQUIRED:
            if item.get(field)!=d.get(field):errors.append("DRIFT_"+stage+"_"+field.upper())
        if item.get("candidate_id") not in (None,selected):errors.append("UNSELECTED_USED_"+stage)
        if selected in ids:
            c=next(c for c in candidates if c.get("candidate_id")==selected)
            if c.get("ai_feasibility")=="PILOT_REQUIRED" and item.get("model_verified") is True:errors.append("PILOT_MISREPRESENTED_"+stage)
    return errors
