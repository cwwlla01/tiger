from pathlib import Path

def audit(text):
    required=['PROPOSED','BLOCKING_REQUIRES_LAYOUT','S09=EDIT_AUDIO_ONLY','S01–S06','S08','左手银戒','平面图']
    missing=[x for x in required if x not in text]
    return {'status':'BLOCKING_REQUIRES_LAYOUT' if not missing else 'INVALID','missing':missing,'other_shots_not_globally_blocked':not missing}

if __name__=='__main__':
    import json
    path=Path(__file__).resolve().parents[1]/'fixtures/v255-contact-blocking/S07-走位方案与生产状态.md'
    print(json.dumps(audit(path.read_text(encoding='utf-8')),ensure_ascii=False))
