"""Verify paired A/B provenance without claiming artistic superiority."""
import hashlib
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(manifest):
    problems=[]
    source=manifest.get("source_path")
    if not source or not Path(source).is_file():
        return {"status":"SOURCE_MISSING","problems":["source_missing"],"quality_improvement_verified":False}
    if sha(source)!=manifest.get("source_sha256"):
        problems.append("source_hash_mismatch")
    hashes={}
    for side in ("baseline","candidate"):
        record=manifest.get(side,{})
        if not record.get("run_id") or not record.get("skill_sha256") or not record.get("execution_log"):
            problems.append(side+"_provenance_incomplete")
        elif not Path(record["execution_log"]).is_file():
            problems.append(side+"_execution_log_missing")
        for stage in ("03","04","05"):
            item=record.get("artifacts",{}).get(stage,{})
            path=item.get("path")
            if not path or not Path(path).is_file():
                problems.append(side+"_"+stage+"_missing")
            elif sha(path)!=item.get("sha256"):
                problems.append(side+"_"+stage+"_hash_mismatch")
            else:
                hashes[(side,stage)]=(str(Path(path).resolve()),sha(path))
    for stage in ("03","04","05"):
        a=hashes.get(("baseline",stage));b=hashes.get(("candidate",stage))
        if a and b and a==b:
            problems.append("identical_artifact_"+stage)
    if manifest.get("baseline",{}).get("run_id") and manifest.get("baseline",{}).get("run_id")==manifest.get("candidate",{}).get("run_id"):
        problems.append("shared_run_id")
    status="PAIRED_PROVENANCE_READY" if not problems else "NOT_VERIFIED"
    return {"status":status,"problems":sorted(problems),"quality_improvement_verified":False}
