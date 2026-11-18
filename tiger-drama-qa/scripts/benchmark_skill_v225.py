"""Conservative, paired text-metric benchmark; no model-quality claims."""
import argparse
import json
from pathlib import Path

def _ratio(n, d):
    return round(n / d, 6) if d else "NOT_VERIFIED"

def metrics(case):
    if not isinstance(case, dict):
        raise ValueError("case must be object")
    src = case.get("source_beat_ids")
    gen = case.get("generated_beat_ids")
    prompts = case.get("prompts")
    if not isinstance(src, list) or not isinstance(gen, list) or not isinstance(prompts, list):
        raise ValueError("source_beat_ids, generated_beat_ids and prompts must be lists")
    if not all(isinstance(x, str) and x.strip() for x in src + gen + prompts):
        raise ValueError("all IDs and prompts must be nonempty strings")
    if len(set(src)) != len(src) or len(set(gen)) != len(gen):
        raise ValueError("beat IDs must be unique")
    s, g = set(src), set(gen)
    norm = [" ".join(x.split()).casefold() for x in prompts]
    qa = case.get("qa_confusion")
    precision = recall = "NOT_VERIFIED"
    if qa is not None:
        if not isinstance(qa, dict) or any(type(qa.get(k)) is not int or qa[k] < 0 for k in ("tp", "fp", "fn")):
            raise ValueError("qa_confusion requires nonnegative integer tp,fp,fn")
        precision = _ratio(qa["tp"], qa["tp"] + qa["fp"])
        recall = _ratio(qa["tp"], qa["tp"] + qa["fn"])
    return {"beat_coverage": _ratio(len(s & g), len(s)),
            "unsupported_addition_ids": sorted(g - s),
            "prompt_redundancy": _ratio(len(norm) - len(set(norm)), len(norm)),
            "mean_prompt_chars": _ratio(sum(map(len, prompts)), len(prompts)),
            "qa_precision": precision, "qa_recall": recall}

def compare(data):
    if not isinstance(data, dict) or not isinstance(data.get("case_id"), str) or not data["case_id"].strip():
        raise ValueError("case_id required")
    if data.get("evidence_level") not in ("FIXTURE_ONLY", "TEXT_REVIEWED", "MODEL_OBSERVED"):
        raise ValueError("valid evidence_level required")
    for key in ("source_sha256", "baseline_version", "candidate_version"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(key + " required")
    if len(data["source_sha256"]) != 64 or any(c not in "0123456789abcdefABCDEF" for c in data["source_sha256"]):
        raise ValueError("invalid SHA256")
    a, b = metrics(data.get("baseline")), metrics(data.get("candidate"))
    if data["baseline"].get("source_beat_ids") != data["candidate"].get("source_beat_ids"):
        raise ValueError("paired source beats differ")
    return {"case_id": data["case_id"], "evidence_level": data["evidence_level"],
            "baseline": a, "candidate": b,
            "production_quality_verified": False if data["evidence_level"] != "MODEL_OBSERVED" else "REQUIRES_INDEPENDENT_REVIEW"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = compare(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
if __name__ == "__main__":
    main()
