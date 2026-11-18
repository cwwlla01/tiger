"""Conservative A/B evidence gate. No content-quality inference."""
import argparse, hashlib, json
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(data):
    if not isinstance(data, dict):
        raise ValueError("manifest must be object")
    for field in ("case_id", "source_path", "source_sha256", "baseline_version", "candidate_version"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(field + " required")
    source = Path(data["source_path"])
    if not source.is_file():
        raise ValueError("source missing")
    if digest(source) != data["source_sha256"]:
        raise ValueError("source hash mismatch")
    missing=[]; resolved={}
    for side in ("baseline", "candidate"):
        arts=data.get(side+"_artifacts", {})
        if not isinstance(arts, dict):
            raise ValueError(side+"_artifacts must be object")
        for stage in ("03", "04", "05"):
            path=arts.get(stage)
            if not path:
                missing.append(side+"_"+stage)
            elif not Path(path).is_file():
                missing.append(side+"_"+stage+"_missing_file")
            else:
                resolved[(side,stage)]=(str(Path(path).resolve()),digest(path))
    collisions=[stage for stage in ("03","04","05") if ("baseline",stage) in resolved and ("candidate",stage) in resolved and resolved[("baseline",stage)][0]==resolved[("candidate",stage)][0]]
    if collisions:
        missing.extend("same_path_"+s for s in collisions)
    provenance=data.get("independent_run_evidence", {})
    if not isinstance(provenance,dict):
        raise ValueError("independent_run_evidence must be object")
    for side in ("baseline","candidate"):
        if not isinstance(provenance.get(side),str) or not provenance[side].strip():
            missing.append(side+"_run_provenance")
    eligible=not missing
    level="PAIRED_TEXT" if eligible else ("BASELINE_ONLY" if all(("baseline",s) in resolved for s in ("03","04","05")) else "SOURCE_ONLY")
    return {"case_id":data["case_id"],"evidence_level":level,"comparison_eligible":eligible,"missing_evidence":sorted(missing),"verified_source_sha256":digest(source),"quality_improvement_verified":False}

def main():
    p=argparse.ArgumentParser();p.add_argument("manifest",type=Path);p.add_argument("--output",type=Path)
    a=p.parse_args(); result=audit(json.loads(a.manifest.read_text(encoding="utf-8")))
    s=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output:a.output.write_text(s,encoding="utf-8")
    else:print(s)
if __name__=="__main__":main()
