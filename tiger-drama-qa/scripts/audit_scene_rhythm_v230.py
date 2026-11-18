"""Conservative structural preflight for scene-level camera rhythm contracts."""
import argparse
import json
from pathlib import Path

REQUIRED = ("scene_id", "shot_id", "source_beat_ids", "dramatic_function", "attention_target", "camera_choice", "entry_state", "exit_state", "cut_reason")
CHOICES = {"STATIC", "MOVE", "CUT", "HOLD"}

def audit(payload):
    issues = []
    shots = payload.get("shots")
    if not isinstance(shots, list) or not shots:
        return {"status": "NOT_VERIFIED", "issues": [{"code": "NO_SHOTS"}], "checked_shots": 0}
    seen = set()
    last = {}
    for i, shot in enumerate(shots):
        if not isinstance(shot, dict):
            issues.append({"code": "INVALID_SHOT", "index": i}); continue
        loc = {"scene_id": shot.get("scene_id"), "shot_id": shot.get("shot_id")}
        for field in REQUIRED:
            if field not in shot or shot[field] is None or shot[field] == "":
                issues.append({"code": "MISSING_FIELD", "field": field, **loc})
        key = (shot.get("scene_id"), shot.get("shot_id"))
        if key in seen: issues.append({"code": "DUPLICATE_SHOT", **loc})
        seen.add(key)
        if shot.get("camera_choice") not in CHOICES:
            issues.append({"code": "INVALID_CAMERA_CHOICE", **loc})
        beats = shot.get("source_beat_ids")
        if not isinstance(beats, list) or not beats or not all(isinstance(b, str) and b for b in beats):
            issues.append({"code": "INVALID_SOURCE_BEATS", **loc})
        scene = shot.get("scene_id")
        if scene in last and shot.get("entry_state") != last[scene].get("exit_state"):
            issues.append({"code": "STATE_DISCONTINUITY", **loc})
        last[scene] = shot
    reveal = payload.get("reveal")
    if reveal is not None:
        if not isinstance(reveal, dict) or not reveal.get("reveal_beat_id") or not reveal.get("reveal_shot_id"):
            issues.append({"code": "INVALID_REVEAL"})
        elif reveal["reveal_shot_id"] not in {s.get("shot_id") for s in shots if isinstance(s,dict)}:
            issues.append({"code": "REVEAL_SHOT_MISSING"})
    return {"status": "FAIL" if issues else "PASS_STRUCTURAL", "issues": issues, "checked_shots": len(shots)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(json.loads(args.input.read_text(encoding="utf-8")))
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output: args.output.write_text(output, encoding="utf-8")
    else: print(output)
    return 0 if result["status"] == "PASS_STRUCTURAL" else 1

if __name__ == "__main__": raise SystemExit(main())
