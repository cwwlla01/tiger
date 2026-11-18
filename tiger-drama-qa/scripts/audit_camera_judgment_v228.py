"""Structural handoff audit for V2.28. Does not assess artistic quality."""
VALID_MODES = {"STATIC", "MOVE", "CUT", "HOLD"}
VALID_FUNCTIONS = {"ESTABLISH_SPACE", "REVEAL_INFORMATION", "OBSERVE_REACTION", "BUILD_TENSION", "PAYOFF_ACTION", "RELEASE_TENSION"}
IMMUTABLE = ("decision_id", "chosen_design_id", "beat_id", "shot_function", "dramatic_intent", "attention_target")

def audit(data):
    errors = []
    source = data.get("03")
    if not isinstance(source, list) or not source:
        return ["MISSING_03"]
    indexed = {}
    for row in source:
        if not isinstance(row, dict):
            errors.append("INVALID_03_RECORD"); continue
        did = row.get("decision_id")
        if not did:
            errors.append("MISSING_DECISION_ID"); continue
        if did in indexed:
            errors.append("DUPLICATE_DECISION_ID:" + did)
        indexed[did] = row
        if not row.get("source_anchor") or not row.get("beat_id"):
            errors.append("MISSING_SOURCE:" + did)
        if not row.get("chosen_design_id"):
            errors.append("MISSING_CHOSEN_DESIGN:" + did)
        if row.get("shot_function") not in VALID_FUNCTIONS:
            errors.append("INVALID_SHOT_FUNCTION:" + did)
        cam = row.get("camera_choice", {})
        if not isinstance(cam, dict) or cam.get("mode") not in VALID_MODES:
            errors.append("INVALID_CAMERA_MODE:" + did)
        elif not cam.get("reason") or not cam.get("observable_payoff"):
            errors.append("MISSING_CAMERA_RATIONALE:" + did)
    for stage in ("04", "05"):
        rows = data.get(stage)
        if not isinstance(rows, list):
            errors.append("MISSING_STAGE:" + stage); continue
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                errors.append("INVALID_RECORD:" + stage); continue
            did = row.get("decision_id")
            if did not in indexed:
                errors.append("UNKNOWN_DECISION:" + stage + ":" + str(did)); continue
            seen.add(did)
            origin = indexed[did]
            for field in IMMUTABLE:
                if row.get(field) != origin.get(field):
                    errors.append("DRIFT:" + stage + ":" + did + ":" + field)
            mode = origin.get("camera_choice", {}).get("mode")
            if row.get("camera_mode") != mode:
                errors.append("CAMERA_MODE_DRIFT:" + stage + ":" + did)
            if stage == "05" and mode == "STATIC" and row.get("dynamic_camera", False):
                errors.append("UNAUTHORIZED_CAMERA_MOTION:" + did)
            if stage == "05" and mode == "CUT" and row.get("continuous_take", False):
                errors.append("CUT_AS_CONTINUOUS_TAKE:" + did)
        for did in indexed.keys() - seen:
            errors.append("MISSING_DECISION:" + stage + ":" + did)
    return errors
