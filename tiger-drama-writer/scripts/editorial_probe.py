#!/usr/bin/env python3
"""Generate auditable voice/runtime/editorial probes, not a quality certificate."""
import argparse,json,re
from collections import defaultdict
from pathlib import Path
from audit_script_batch import EP,SC,SPEECH,han

ACTION_VERBS='拿推按拉扯递撕摔挡抱放退撞锁拆合盖签敲举攥握冲走转掀藏收递停'
EMOTION_TERMS='怕疼恨哭笑怒悔信求爱失望后悔对不起别走答应抱歉'

def probe(path, chars_per_minute=260, pause_seconds_per_scene=8):
    text=Path(path).read_text(encoding='utf-8'); matches=list(EP.finditer(text)); episodes=[]
    for i,m in enumerate(matches):
        part=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        scene_heads=list(SC.finditer(part)); dialogues=list(SPEECH.finditer(part)); speakers=defaultdict(list)
        for d in dialogues:
            speakers[(d.group(1) or d.group(2)).strip()].append(d.group(3).strip())
        speech_han=sum(han(x.group(3)) for x in dialogues)
        nonspoken=part
        for d in reversed(dialogues): nonspoken=nonspoken[:d.start()]+nonspoken[d.end():]
        action_han=han(nonspoken)
        # A wide estimate, never a measured running time; pauses and blocking need rehearsal.
        base_minutes=speech_han/chars_per_minute
        low=round((speech_han/320 + len(scene_heads)*4/60),2)
        high=round((speech_han/200 + len(scene_heads)*20/60),2)
        profiles=[]
        for name,lines in sorted(speakers.items(),key=lambda x:-len(x[1])):
            lengths=[han(s) for s in lines]; joined=' '.join(lines)
            profiles.append({'name':name,'turns':len(lines),'mean_line_han':round(sum(lengths)/len(lengths),1),'question_ratio':round(sum('？' in s or '?' in s for s in lines)/len(lines),2),'command_ratio':round(sum(any(k in s for k in ('别','快','必须','立刻','给我')) for s in lines)/len(lines),2),'sample_lines':lines[:3]})
        episode={'episode':int(m.group(1)),'scenes':len(scene_heads),'spoken_han':speech_han,'non_dialogue_han':action_han,'speech_to_action_ratio':round(speech_han/max(action_han,1),2),'estimated_minutes_low_high':[low,high], 'timed_readthrough':False,'speakers':profiles,'editorial_review_required':['Blind-remove speaker names from at least six lines per major role and judge distinguishability.','Identify concrete on-page decision, emotional consequence and carryover; cite actual scene lines.','Estimate includes generic speech and pause assumptions; measure read-through to verify.']}
        if len(scene_heads)==0: episode['warning']='NO_SCENES'
        episodes.append(episode)
    return {'file':str(path),'assumptions':{'spoken_han_per_minute_range':[200,320],'pause_seconds_per_scene_range':[4,20]},'episodes':episodes,'quality_certified':False}

if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('file');a.add_argument('--output'); args=a.parse_args()
    result=probe(args.file); s=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:Path(args.output).write_text(s,encoding='utf-8')
    print(s)
