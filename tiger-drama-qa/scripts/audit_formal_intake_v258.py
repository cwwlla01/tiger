import json,sys
from pathlib import Path
REQUIRED=("authoritative_script","script_version","asset_manifest","storyboard_03","static_prompts_04","video_prompts_05","independent_qa_06")
def audit(data):
    missing=[k for k in REQUIRED if not data.get(k)]
    if data.get("source_type")!="FORMAL_AUTHORITY" or not data.get("authoritative_script"):
        status="GLOBAL_SOURCE_BLOCK"
    elif missing:
        status="FORMAL_INTAKE_INCOMPLETE"
    elif not data.get("video_evidence"):
        status="TEXT_INTAKE_COMPLETE_VIDEO_UNTESTED"
    else:
        status="EVIDENCE_SUBMITTED_REQUIRES_INDEPENDENT_REVIEW"
    return {"status":status,"missing":missing,"local_blocks":data.get("known_local_blocks",[]),"video_verified":False,"production_accepted":False}
if __name__=="__main__":
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent.parent/"fixtures/v258-formal-intake/formal_project_manifest.json"
    print(json.dumps(audit(json.loads(path.read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
