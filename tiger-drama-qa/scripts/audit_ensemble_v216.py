#!/usr/bin/env python3
"""V2.16 ensemble beat handoff structural checker; not a cinematic quality judge."""
import json,sys
from pathlib import Path
FIELDS=("present_characters","attention_anchor","active_speaker","information_holders","reaction_targets","blocking_state","screen_axis","reveal_order")
def audit(bundle):
    errors=[]; stages=bundle.get("stages",{})
    if any(s not in stages for s in ("03","04","05")):
        return ["NOT_VERIFIED: missing 03/04/05 stage"]
    indexed={}
    for stage in ("03","04","05"):
        beats=stages[stage].get("beats")
        if not isinstance(beats,list):
            errors.append(f"{stage}: beats missing or invalid");continue
        ids={}
        for b in beats:
            if not isinstance(b,dict) or not b.get("beat_id"):
                errors.append(f"{stage}: missing beat_id");continue
            key=b["beat_id"]
            if key in ids: errors.append(f"{stage}/{key}: duplicate beat_id")
            ids[key]=b
            if stage=="03":
                for f in FIELDS:
                    if f not in b:errors.append(f"03/{key}: missing {f}")
                present=b.get("present_characters",[])
                if not isinstance(present,list) or len(set(present))<3:
                    errors.append(f"03/{key}: expected 3+ distinct characters")
                else:
                    if b.get("active_speaker") is not None and b.get("active_speaker") not in present:
                        errors.append(f"03/{key}: speaker absent")
                    for f in ("information_holders","reaction_targets"):
                        if not isinstance(b.get(f),list) or any(x not in present for x in b[f]):
                            errors.append(f"03/{key}: invalid {f}")
                    anchor=b.get("attention_anchor")
                    if anchor not in present and not (isinstance(anchor,str) and anchor.startswith("PROP-")):
                        errors.append(f"03/{key}: attention anchor not grounded")
        indexed[stage]=ids
    if "03" not in indexed:return errors
    source=indexed["03"]
    for stage in ("04","05"):
        if stage not in indexed:continue
        other=indexed[stage]
        for key in sorted(set(source)-set(other)):errors.append(f"{stage}/{key}: missing beat")
        for key in sorted(set(other)-set(source)):errors.append(f"{stage}/{key}: extra beat")
        for key in sorted(set(source)&set(other)):
            for f in FIELDS:
                if source[key].get(f)!=other[key].get(f):errors.append(f"{stage}/{key}: drift {f}")
    return errors
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: audit_ensemble_v216.py bundle.json")
    result=audit(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print(json.dumps({"passed":not result,"errors":result},ensure_ascii=False,indent=2))
    raise SystemExit(bool(result))
