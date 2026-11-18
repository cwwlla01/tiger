"""Structural-only 03/05 performance-camera contract check."""
import argparse
import json
from pathlib import Path

REQUIRED = ("source_beat_id", "performance_trigger", "camera_response", "response_timing", "attention_target", "exit_state")
RESPONSES = {"STATIC", "MOVE", "CUT", "HOLD"}
TIMINGS = {"BEFORE", "DURING", "AFTER", "NONE"}

def audit(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("director"), list) or not isinstance(payload.get("video"), list):
        return {"status": "NOT_VERIFIED", "issues": [{"code": "MISSING_PAIR"}], "checked": 0}
    director, video = payload["director"], payload["video"]
    if not director or not video:
        return {"status": "NOT_VERIFIED", "issues": [{"code": "EMPTY_PAIR"}], "checked": 0}
    issues = []
    def index(items, side):
        out = {}
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                issues.append({"code": "INVALID_RECORD", "side": side, "index": i}); continue
            key = item.get("source_beat_id")
            if not isinstance(key, str) or not key:
                issues.append({"code": "MISSING_BEAT_ID", "side": side, "index": i}); continue
            if key in out: issues.append({"code": "DUPLICATE_BEAT", "side": side, "beat": key})
            out[key] = item
            for field in REQUIRED:
                if not isinstance(item.get(field), str) or not item[field].strip():
                    issues.append({"code": "MISSING_FIELD", "side": side, "beat": key, "field": field})
            if item.get("camera_response") not in RESPONSES:
                issues.append({"code": "INVALID_RESPONSE", "side": side, "beat": key})
            if item.get("response_timing") not in TIMINGS:
                issues.append({"code": "INVALID_TIMING", "side": side, "beat": key})
        return out
    d = index(director, "director"); v = index(video, "video")
    for key in sorted(d.keys() - v.keys()): issues.append({"code": "MISSING_VIDEO_BEAT", "beat": key})
    for key in sorted(v.keys() - d.keys()): issues.append({"code": "UNAUTHORIZED_VIDEO_BEAT", "beat": key})
    for key in sorted(d.keys() & v.keys()):
        for field in REQUIRED[1:]:
            if d[key].get(field) != v[key].get(field):
                issues.append({"code": "FIELD_DRIFT", "beat": key, "field": field})
    return {"status": "FAIL" if issues else "PASS_STRUCTURAL", "issues": issues, "checked": len(d)}

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
