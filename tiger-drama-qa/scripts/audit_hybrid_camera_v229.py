"""Static handoff audit. Does not evaluate artistic quality."""
VALID={"STATIC","HOLD","MOVE","CUT"}
def audit(records):
    issues=[]
    for index,r in enumerate(records):
        sid=r.get("shot_id",str(index))
        choice=r.get("camera_choice")
        if choice not in VALID:
            issues.append((sid,"INVALID_CAMERA_CHOICE"));continue
        for field in ("dramatic_intent","audience_information","attention_target"):
            if not str(r.get(field,"")).strip():issues.append((sid,"MISSING_"+field.upper()))
        compiled=r.get("compiled_camera_choice")
        if compiled is not None and compiled!=choice:issues.append((sid,"UNAUTHORIZED_CAMERA_CHANGE"))
        if choice=="MOVE" and not r.get("motion_path"):
            issues.append((sid,"MISSING_MOTION_PATH"))
        if choice=="CUT" and r.get("single_continuous_take") is True:
            issues.append((sid,"CUT_IN_CONTINUOUS_TAKE"))
        if r.get("reveal_before_source") is True:
            issues.append((sid,"PREMATURE_REVEAL"))
    return issues
