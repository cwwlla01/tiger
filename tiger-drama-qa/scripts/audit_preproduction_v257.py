import json,sys
from pathlib import Path

def audit(path):
 p=json.loads(Path(path).read_text(encoding="utf-8")); s={x["id"]:x for x in p["shots"]}; errors=[]
 for key in ("S01B","S04","S06","S07","S09"):
  if key not in s: errors.append("missing:"+key)
 if errors:return {"status":"INVALID","errors":errors}
 if s["S01B"].get("route")!="PLATE_PLUS_POST_TEXT" or s["S01B"].get("exact_text")!="第三声后别回头":errors.append("text_overlay")
 if s["S04"].get("reveal_outside") is not False or s["S04"].get("order")!="SECOND_KNOCK_BEFORE_VOICE":errors.append("offscreen_voice")
 if s["S06"].get("reveal_identity") is not False or s["S06"].get("door_open") is not False:errors.append("identity_leak")
 if s["S07"].get("status")!="LAYOUT_BLOCKED" or len(s["S07"].get("required",[]))<3:errors.append("layout_claim")
 if s["S09"].get("route")!="EDIT_AUDIO_ONLY" or s["S09"].get("order")!="BLACK_BEFORE_THIRD_KNOCK":errors.append("black_audio")
 for k in ("asset_status","model_status","video_status"):
  if p.get(k) not in ("ASSET_UNVERIFIED","MODEL_UNVERIFIED","VIDEO_NOT_TESTED"):errors.append("false_verification:"+k)
 return {"status":"TEXT_PLAN_COMPLETE_WITH_LAYOUT_BLOCK" if not errors else "INVALID","errors":errors,"blocked_shots":["S07"]}
if __name__=="__main__":print(json.dumps(audit(sys.argv[1]),ensure_ascii=False))
