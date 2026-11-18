"""Conservative structural comparison of director/video ensemble beats."""
import argparse
import json
from pathlib import Path

FIELDS = ("scene_id", "beat_id", "speaking_character", "dramatic_controller", "attention_target", "relationship_shift", "gaze_axis", "camera_choice", "cut_motivation", "reaction_beat", "exit_state")
CHOICES = {"STATIC", "MOVE", "CUT", "HOLD"}

def audit(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("director"), list) or not isinstance(payload.get("video"), list) or not payload["director"] or not payload["video"]:
        return {"status": "NOT_VERIFIED", "issues": [{"code": "MISSING_PAIR"}], "checked": 0}
    issues = []
    def build(items, side):
        index = {}
        for pos, item in enumerate(items):
            if not isinstance(item, dict):
                issues.append({"code": "INVALID_RECORD", "side": side, "index": pos}); continue
            key = (item.get("scene_id"), item.get("beat_id"))
            if not all(isinstance(x, str) and x.strip() for x in key):
                issues.append({"code": "MISSING_ID", "side": side, "index": pos}); continue
            if key in index:
                issues.append({"code": "DUPLICATE_BEAT", "side": side, "beat": list(key)})
            index[key] = item
            for field in FIELDS:
                if not isinstance(item.get(field), str) or not item[field].strip():
                    issues.append({"code": "MISSING_FIELD", "side": side, "beat": list(key), "field": field})
            if item.get("camera_choice") not in CHOICES:
                issues.append({"code": "INVALID_CHOICE", "side": side, "beat": list(key)})
            if item.get("camera_choice") == "CUT" and item.get("cut_motivation") == "NONE":
                issues.append({"code": "UNMOTIVATED_CUT", "side": side, "beat": list(key)})
        return index
    d = build(payload["director"], "director"); v = build(payload["video"], "video")
    for key in sorted(d.keys()-v.keys()): issues.append({"code": "MISSING_VIDEO_BEAT", "beat": list(key)})
    for key in sorted(v.keys()-d.keys()): issues.append({"code": "UNAUTHORIZED_VIDEO_BEAT", "beat": list(key)})
    for key in sorted(d.keys() & v.keys()):
        for field in FIELDS:
            if d[key].get(field) != v[key].get(field):
                issues.append({"code": "FIELD_DRIFT", "beat": list(key), "field": field})
    return {"status": "FAIL" if issues else "PASS_STRUCTURAL", "issues": issues, "checked": len(d)}

def main():
    p = argparse.ArgumentParser(); p.add_argument("input", type=Path); p.add_argument("--output", type=Path); a=p.parse_args()
    result=audit(json.loads(a.input.read_text(encoding="utf-8"))); output=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output: a.output.write_text(output,encoding="utf-8")
    else: print(output)
    return 0 if result["status"]=="PASS_STRUCTURAL" else 1

if __name__ == "__main__": raise SystemExit(main())
