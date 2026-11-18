#!/usr/bin/env python3
"""V2.63 conservative intent/channel/shot-group gate. TEXT audit, not video QA.

Input is a compact plan manifest that lives OUTSIDE the copyable Seedance prompt.
"""
from __future__ import annotations
import argparse
import math
import re
import json
from pathlib import Path

FIXTURE_IDS = {"bridge_rescue", "person_behind_door", "rain_farewell", "operating_room", "shelter_vote", "mountain_dragon"}
BENEFITS = {"continuous_actor_performance", "motivated_viewpoint_change", "inseparable_causal_event", "matched_visual_reveal"}
PROOF = {"user_interface_verified", "official_exact_channel", "official_other_channel", "series_only", "unknown"}


def _text(v):
    return isinstance(v, str) and len(v.strip()) >= 12 and v.strip().lower() not in {"none", "n/a", "tbd", "unknown", "same", "save money", "saves calls", "less cost"}


def audit(m):
    errors, notices = [], []
    intent = m.get("intent")
    if intent not in {"description", "storyboard", "seedance_prompt"}:
        return {"status":"FAIL", "errors":["E-INTENT: missing explicit output intent"], "notices":[]}
    takes = m.get("takes", [])
    if intent == "description":
        if takes or m.get("duration_policy", {}).get("selected_seconds") is not None:
            errors.append("E-DESCRIPTION-LEAK: prose description cannot inherit video takes/duration")
        if m.get("delivery_type") != "description":
            errors.append("E-OUTPUT-TYPE: user requested description, not storyboard/video")
        return {"status":"FAIL" if errors else "TEXT_ROUTE_PASS", "errors":errors, "notices":notices}
    if intent == "storyboard":
        if m.get("delivery_type") != "storyboard":
            errors.append("E-OUTPUT-TYPE: storyboard must not silently become video prompt")
        if m.get("duration_policy", {}).get("origin") == "legacy_fixture_default":
            errors.append("E-DURATION-FIXTURE: old 15s fixture not a global duration")
        return {"status":"FAIL" if errors else "TEXT_ROUTE_PASS", "errors":errors, "notices":notices}

    if m.get("delivery_type") != "seedance_prompt":
        errors.append("E-OUTPUT-TYPE: wrong final artifact")
    channel = m.get("channel") or {}
    platform = channel.get("platform")
    model = channel.get("model_display_name", "")
    proof = channel.get("proof_scope", "unknown")
    multishot_proof = channel.get("multishot_proof", "unverified")
    if platform not in {"jimeng_web", "volc_ark_api"}:
        errors.append("E-CHANNEL: exact Seedance channel not identified")
    if not re.search(r"seedance\s*2(?:\.0)?\s*fast\b",model,re.I):
        errors.append("E-MODEL: selected model must explicitly be Seedance 2 Fast")
    if platform == "volc_ark_api" and channel.get("model_id") != "doubao-seedance-2-0-fast-260128":
        errors.append("E-MODEL-ID: incorrect Volc Ark Seedance 2.0 Fast ID")
    if platform == "jimeng_web" and channel.get("model_id"):
        errors.append("E-CHANNEL-MIX: API model ID cannot be presented as Jimeng UI selection")
    if proof not in PROOF:
        errors.append("E-EVIDENCE-SCOPE: unrecognized channel evidence scope")
    if proof in {"user_interface_verified", "official_exact_channel"} and not _text(channel.get("evidence", "")):
        errors.append("E-EVIDENCE: verified channel requires attributable evidence")
    status = m.get("delivery_status", "CANDIDATE")
    if status not in {"CANDIDATE", "SUBMIT_READY"}:
        errors.append("E-STATUS: allowed values CANDIDATE or SUBMIT_READY")
    if status == "SUBMIT_READY" and proof not in {"user_interface_verified", "official_exact_channel"}:
        errors.append("E-SUBMIT-READY: same-channel evidence required")
    if multishot_proof not in {"same_channel_verified", "other_channel_verified", "series_only", "unverified"}:
        errors.append("E-MULTISHOT-PROOF: invalid level")

    duration = m.get("duration_policy") or {}
    seconds = duration.get("selected_seconds")
    requested = duration.get("user_requested_seconds")
    origin = duration.get("origin")
    fixture = m.get("fixture_id")
    if isinstance(seconds,bool) or not isinstance(seconds, (int,float)) or not math.isfinite(seconds) or seconds <= 0:
        errors.append("E-DURATION: positive scene-specific target required")
    if origin not in {"user_requested", "dramatic_pacing", "verified_channel_choice", "fixture_15s"}:
        errors.append("E-DURATION-ORIGIN: fixed default or unknown basis")
    if origin == "fixture_15s" and fixture not in FIXTURE_IDS:
        errors.append("E-FIXTURE-LEAK: six-case 15s rule outside six fixtures")
    if origin == "user_requested" and (requested is None or seconds != requested):
        errors.append("E-USER-DURATION: user requested value must be respected")
    if origin == "dramatic_pacing" and not _text(duration.get("reason", "")):
        errors.append("E-DURATION-REASON: derive length from visible action and hold")
    allowed = channel.get("supported_durations_s", [])
    # The scene's final film duration is NOT the model's per-generation duration.
    # A 15s film may be edited from 8s and 10s generations, for instance.
    if not allowed or proof in {"unknown", "series_only", "official_other_channel"}:
        notices.append("N-CHANNEL-UNVERIFIED: prompt is text candidate, channel settings are not proved")

    shots = m.get("editorial_shots") or []
    expected = [s.get("id") for s in shots]
    if not expected or any(not isinstance(i,str) or not i.startswith("SH") for i in expected):
        errors.append("E-SHOTS: source editorial shots not provided")
    if len(set(expected)) != len(expected):
        errors.append("E-SHOTS-DUPLICATE")
    observed = []
    if not takes:
        errors.append("E-TAKE-EMPTY")
    for take in takes:
        tid = take.get("id", "<unnamed>")
        sh = take.get("shot_ids") or []
        observed += sh
        merged = len(sh) > 1
        mode = take.get("grouping", "")
        if merged and mode != "MERGE":
            errors.append(f"{tid} E-MERGE-UNDECLARED")
        if not merged and mode != "SINGLE":
            errors.append(f"{tid} E-SINGLE-MODE: single-shot must not be called merge")
        prompt=take.get("prompt") if isinstance(take.get("prompt"),str) else ""
        if not _text(prompt):
            errors.append(f"{tid} E-PROMPT-MISSING")
        if any(x in prompt for x in ("PLACEHOLDER", "@image1", "@image2", "@图片1")) and not take.get("references_uploaded_and_grammar_verified", False):
            errors.append(f"{tid} E-UNVERIFIED-ASSET-TOKEN")
        generated=take.get("generated_seconds")
        if not isinstance(generated,(int,float)) or generated <= 0:
            errors.append(f"{tid} E-TAKE-DURATION: missing positive per-generation duration")
        if allowed and isinstance(generated,(int,float)) and generated not in allowed:
            if status == "SUBMIT_READY":
                errors.append(f"{tid} E-CHANNEL-DURATION: generation is not an observed channel duration choice")
            else:
                notices.append(f"{tid} N-CHANNEL-DURATION: adapt per-generation seconds to actual UI options")
        edit_in=take.get("edit_in_seconds")
        edit_out=take.get("edit_out_seconds")
        if edit_in is not None or edit_out is not None:
            if not all(isinstance(v,(int,float)) for v in (edit_in, edit_out, generated)) or not (0<=edit_in<edit_out<=generated):
                errors.append(f"{tid} E-EDIT-TRIM: invalid retained edit range")
        if not merged:
            if take.get("merge_decision"):
                errors.append(f"{tid} E-UNNECESSARY-MERGE-DATA")
            continue
        for shot_id in sh:
            if shot_id not in prompt:
                errors.append(f"{tid} E-MERGED-PROMPT-SHOT: {shot_id} omitted from actual copy text")
        if not any(w in prompt for w in ("HARD_CUT", "MATCH_CUT", "CONTINUOUS_CAMERA", "OCCLUSION_CUT", "\u786c\u5207", "\u5339\u914d\u5207", "\u8fde\u7eed\u8fd0\u955c")):
            errors.append(f"{tid} E-MERGED-PROMPT-CUT: transitions missing in actual copy text")
        if "00:" not in prompt:
            errors.append(f"{tid} E-MERGED-PROMPT-TIME: actual copy text lacks timed shots")
        if multishot_proof == "same_channel_verified" and not _text(channel.get("multishot_evidence", "")):
            errors.append(f"{tid} E-MULTISHOT-EVIDENCE: exact-channel multishot claim needs source")
        decision = take.get("merge_decision") or {}
        if decision.get("benefit") not in BENEFITS:
            errors.append(f"{tid} E-MERGE-BENEFIT: technical capability/cost is not a dramatic reason")
        if not _text(decision.get("specific_gain", "")):
            errors.append(f"{tid} E-MERGE-GAIN: explain what viewer gains from this particular grouping")
        boundaries = decision.get("boundaries") or []
        if len(boundaries) != len(sh)-1:
            errors.append(f"{tid} E-MERGE-BOUNDARY-COUNT")
        for k, pair in enumerate(zip(sh,sh[1:])):
            if k >= len(boundaries): break
            b = boundaries[k]
            if (b.get("from"), b.get("to")) != pair:
                errors.append(f"{tid} E-MERGE-BOUNDARY-ID: must identify adjacent source shots")
            if not _text(b.get("dramatic_reason", "")):
                errors.append(f"{tid} E-MERGE-DRAMA: no specific narrative cause at {pair}")
            if not _text(b.get("continuity_evidence", "")):
                errors.append(f"{tid} E-MERGE-CONTINUITY: no space/light/identity evidence at {pair}")
            if not _text(b.get("risk_mitigation", "")):
                errors.append(f"{tid} E-MERGE-RISK: no execution fallback at {pair}")
            if b.get("transition") not in {"HARD_CUT","MATCH_CUT","OCCLUSION_CUT","CONTINUOUS_CAMERA"}:
                errors.append(f"{tid} E-MERGE-TRANSITION: unplanned camera transition at {pair}")
            if b.get("risk_level") not in {"LOW", "MEDIUM", "HIGH"}:
                errors.append(f"{tid} E-MERGE-RISK-LEVEL: expected LOW/MEDIUM/HIGH")
            if b.get("risk_level") == "HIGH" and not b.get("pilot_observed"):
                errors.append(f"{tid} E-MERGE-HIGH-RISK: separate takes until actual pilot evidence")
            if b.get("conflicting_references") and not b.get("reference_strategy_verified"):
                errors.append(f"{tid} E-MERGE-REFERENCES: incompatible inputs must not be lumped together")
        timeline=take.get("shot_timeline") or []
        if len(timeline)!=len(sh):
            errors.append(f"{tid} E-MULTISHOT-TIMELINE: every SH requires local time interval")
        else:
            cursor=0.0
            for segment,shot in zip(timeline,sh):
                start,end=segment.get("start"),segment.get("end")
                if segment.get("shot_id")!=shot or not isinstance(start,(int,float)) or not isinstance(end,(int,float)) or abs(start-cursor)>.05 or end<=start:
                    errors.append(f"{tid} E-MULTISHOT-TIMELINE-CONTINUITY")
                    break
                cursor=end
            if not isinstance(generated,(int,float)) or abs(cursor - generated)>.05:
                errors.append(f"{tid} E-MULTISHOT-TIMELINE-END")
        if multishot_proof != "same_channel_verified":
            notices.append(f"{tid} N-MULTISHOT-PILOT: multi-shot on the exact channel not verified")
            if status == "SUBMIT_READY":
                errors.append(f"{tid} E-CHANNEL-SUBMIT-MERGE: need channel-specific multishot proof")
        if not take.get("pilot_observed", False) and status == "SUBMIT_READY" and multishot_proof != "same_channel_verified":
            errors.append(f"{tid} E-PILOT-MISSING")
    if observed != expected:
        errors.append("E-SHOT-COVERAGE: editorial shot order/uniqueness changed")
    return {"status":"FAIL" if errors else "TEXT_ROUTE_PASS", "errors":errors, "notices":list(dict.fromkeys(notices)), "evidence":"TEXT_ONLY; NOT_CHANNEL_UI_EXECUTION; NOT_VIDEO_QA"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("plan_json")
    p.add_argument("--json-out")
    args=p.parse_args()
    res=audit(json.loads(Path(args.plan_json).read_text(encoding="utf-8")))
    output=json.dumps(res,indent=2,ensure_ascii=False)
    print(output)
    if args.json_out: Path(args.json_out).write_text(output+"\n",encoding="utf-8")
    return int(res["status"]=="FAIL")

if __name__=="__main__": raise SystemExit(main())
