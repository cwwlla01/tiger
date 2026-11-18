"""Conservative 03->05 reveal-rhythm structural audit. No artistic quality inference."""
import argparse
import json
from pathlib import Path

MODES = {'AUDIENCE_AHEAD', 'CHARACTER_AHEAD', 'SHARED_DISCOVERY'}
REQUIRED = ('source_beat_id', 'knowledge_mode', 'reveal_event_id', 'camera_decision', 'cut_trigger')

def audit(data):
    issues=[]
    d=data.get('director',[]); v=data.get('video',[])
    if not isinstance(d,list) or not isinstance(v,list):
        return {'status':'INVALID_INPUT','issues':[{'code':'INVALID_LIST'}],'evidence_level':'STRUCTURE_ONLY'}
    def index(rows,side):
        result={}
        for n,row in enumerate(rows):
            if not isinstance(row,dict):
                issues.append({'code':'INVALID_ROW','side':side,'index':n});continue
            key=row.get('source_beat_id')
            if not key:
                issues.append({'code':'MISSING_ID','side':side,'index':n});continue
            if key in result:issues.append({'code':'DUPLICATE_ID','side':side,'id':key})
            else:result[key]=row
            for field in REQUIRED:
                if not row.get(field):issues.append({'code':'MISSING_FIELD','side':side,'id':key,'field':field})
            if row.get('knowledge_mode') and row['knowledge_mode'] not in MODES:
                issues.append({'code':'INVALID_KNOWLEDGE_MODE','side':side,'id':key})
        return result
    a=index(d,'director');b=index(v,'video')
    for key,row in a.items():
        if key not in b:
            issues.append({'code':'MISSING_VIDEO_BEAT','id':key});continue
        target=b[key]
        for field in ('knowledge_mode','reveal_event_id','reaction_beat_id','camera_decision','cut_trigger','sound_strategy'):
            if row.get(field)!=target.get(field):issues.append({'code':'HANDOFF_DRIFT','id':key,'field':field})
        if row.get('reveal_order') is not None and target.get('reveal_order') is not None and row['reveal_order']!=target['reveal_order']:
            issues.append({'code':'REVEAL_ORDER_DRIFT','id':key})
    for key in b.keys()-a.keys():issues.append({'code':'UNSOURCED_VIDEO_BEAT','id':key})
    return {'status':'FAIL' if issues else 'STRUCTURE_PASS','issues':issues,'evidence_level':'STRUCTURE_ONLY','artistic_quality':'NOT_VERIFIED'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    x=p.parse_args();result=audit(json.loads(Path(x.input).read_text(encoding='utf-8')))
    Path(x.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
