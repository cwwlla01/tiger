"""V2.33 deterministic evidence gate for scene-level A/B storyboard comparisons."""
import argparse,json,hashlib
from pathlib import Path
REQUIRED={"source_beat_id","shot_id","focus_character","dramatic_function","cut_trigger","screen_axis","new_information","duration_estimate"}
def evaluate(record):
 errors=[]
 for k in ("source_sha256","asset_version","candidates"):
  if not record.get(k):errors.append("MISSING_"+k.upper())
 candidates=record.get("candidates",{})
 if not isinstance(candidates,dict) or set(candidates)!={"A","B"}:errors.append("REQUIRE_TWO_CANDIDATES");return {"status":"INCOMPARABLE","errors":errors}
 beats=[]
 for key,c in candidates.items():
  if c.get("source_sha256")!=record.get("source_sha256") or c.get("asset_version")!=record.get("asset_version"):errors.append(key+"_INPUT_MISMATCH")
  shots=c.get("shots",[])
  if not shots:errors.append(key+"_EMPTY_SHOTS")
  ids=[]
  for i,shot in enumerate(shots):
   if not isinstance(shot,dict):errors.append(key+"_BAD_SHOT");continue
   missing=REQUIRED-set(shot)
   if missing:errors.append(key+"_MISSING_FIELDS_"+str(i))
   if shot.get("source_beat_id"):ids.append(shot["source_beat_id"])
  beats.append(set(ids))
 if len(beats)==2 and beats[0]!=beats[1]:errors.append("BEAT_COVERAGE_MISMATCH")
 if errors:return {"status":"INCOMPARABLE","errors":errors}
 review=record.get("blind_review")
 if not review or not isinstance(review,dict) or not review.get("independent_reviewers") or not review.get("dimension_evidence"):
  return {"status":"STRUCTURE_ONLY","errors":[],"note":"No validated blind human comparison"}
 return {"status":"REVIEW_RECORDED_NOT_ART_PROVEN","errors":[],"note":"Review exists; artistic superiority needs human interpretation"}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output');a=ap.parse_args()
 result=evaluate(json.loads(Path(a.input).read_text(encoding='utf-8')))
 out=json.dumps(result,ensure_ascii=False,indent=2)
 if a.output:Path(a.output).write_text(out,encoding='utf-8')
 else:print(out)
if __name__=='__main__':main()
