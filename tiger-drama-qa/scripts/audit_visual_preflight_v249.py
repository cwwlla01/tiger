"""V2.49 textual preflight; NEVER claims visual verification."""
import json, re, sys
from pathlib import Path

def audit(data):
    errors=[]; missing=[]
    shots=data.get("shots",[])
    ids=[s.get("shot_id") for s in shots]
    if not shots or len(ids)!=len(set(ids)): errors.append("missing_or_duplicate_shot_ids")
    if data.get("studio_project_id") is None: missing.append("studio_project_id")
    if not data.get("approved_identity_version"): missing.append("approved_identity_version")
    slots=data.get("approved_scene_slot_ids") or {}
    for s in shots:
        sid=s.get("shot_id")
        if not s.get("beat_id"): errors.append(f"{sid}:missing_beat")
        if s.get("interior_visible") is not False: errors.append(f"{sid}:premature_interior_reveal")
        if s.get("screen_axis")!="same_axis": errors.append(f"{sid}:axis_not_preserved")
        if not slots.get(sid): missing.append(f"{sid}:existing_image_slot")
        if not re.fullmatch(r"[0-9a-f]{64}",s.get("image_sha256") or ""): missing.append(f"{sid}:rendered_image_hash")
    byid={s.get("shot_id"):s for s in shots}
    if "S03" in byid and "S04" in byid:
        if byid["S03"].get("end")!=byid["S04"].get("start"): errors.append("S03_to_S04_hand_state_mismatch")
        if byid["S04"].get("start")!="hand_gripping_unturned_knob": errors.append("S04_first_frame_premature_release")
        if byid["S04"].get("sound_stops_before_release") is not True: errors.append("S04_sound_action_order")
    if errors: status="TEXT_PREFLIGHT_FAILED"
    elif missing: status="PRE_RENDER_BLOCKED"
    else: status="VISUAL_REVIEW_REQUIRED"
    return {"status":status,"errors":errors,"missing_evidence":missing,"visual_verified":False,"shot_count":len(shots)}

if __name__=="__main__":
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(audit(data),ensure_ascii=False,indent=2))
