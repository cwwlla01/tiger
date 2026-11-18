"""Conservative structural checks for V2.24 routing; not artistic review."""
MANDATORY = ("source_anchor", "scene_id", "shot_id", "take_id", "beat_ids", "authority_version")
ALLOWED_EMPTY = {"NOT_APPLICABLE", "NOT_VERIFIED"}

def audit(record):
    errors=[]
    if not isinstance(record,dict): return ["INVALID_RECORD"]
    for key in MANDATORY:
        if key not in record or record[key] is None or record[key]=="": errors.append("MISSING_"+key.upper())
    if "beat_ids" in record and (not isinstance(record["beat_ids"],list) or not record["beat_ids"]): errors.append("INVALID_BEAT_IDS")
    for key in ("asset_versions","knowledge_state","start_state","end_state","camera_intent","sound_boundary"):
        if key in record and record[key] in (None, ""): errors.append("BLANK_"+key.upper())
    if record.get("stage") in ("04","05") and not record.get("director_authority_id"): errors.append("MISSING_DIRECTOR_AUTHORITY")
    if record.get("stage")=="06" and record.get("modifies_authority") is True: errors.append("QA_MODIFIES_AUTHORITY")
    if record.get("model_verified") is True and not record.get("model_evidence"): errors.append("UNSUPPORTED_MODEL_CLAIM")
    if record.get("alias_used") and not record.get("alias_mapping_source"): errors.append("UNTRACED_ALIAS")
    return errors
