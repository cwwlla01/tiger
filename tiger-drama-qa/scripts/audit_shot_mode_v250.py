"""V2.50 route selection validation; no claim of actual visual evidence."""
from __future__ import annotations
MODES = {"TEXT_TO_VIDEO": (), "REFERENCE_TO_VIDEO": ("reference",), "FIRST_FRAME_TO_VIDEO": ("first_frame",), "FIRST_LAST_FRAME_TO_VIDEO": ("first_frame", "last_frame")}

def validate_route(route):
    mode = route.get("mode")
    if mode not in MODES:
        return {"status":"ROUTE_INVALID", "missing": ["mode"]}
    supported = route.get("supported_modes")
    if not isinstance(supported, list) or mode not in supported:
        return {"status":"ROUTE_CAPABILITY_UNVERIFIED", "missing": ["model_support"]}
    missing = [name for name in MODES[mode] if not route.get("inputs", {}).get(name, {}).get("verified", False)]
    return {"status": "ROUTE_INPUT_BLOCKED" if missing else "ROUTE_READY_TEXT_ONLY", "missing": missing}

def audit_routes(routes):
    return {str(r.get("shot", i)):validate_route(r) for i,r in enumerate(routes)}
