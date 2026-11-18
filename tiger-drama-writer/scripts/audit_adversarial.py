#!/usr/bin/env python3
"""Conservative anti-padding diagnostics; never certifies screenplay quality."""
import argparse, json, re
from collections import Counter
from pathlib import Path
from audit_script_batch import EP, SC, SPEECH, han

def inspect(path, *, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH, source_text=None):
    s=source_text if source_text is not None else Path(path).read_text(encoding='utf-8'); matches=list(episode_pattern.finditer(s)); result=[]
    for i,m in enumerate(matches):
        body=s[m.end():matches[i+1].start() if i+1<len(matches) else len(s)]
        body=re.split(r'^---\s*\n\s*##\s*(?:附录|验收|审稿|质量|续写|状态|附注)',body,maxsplit=1,flags=re.M)[0]
        speeches=speech_pattern.findall(body); speech_text=[re.sub(r'\s+','',x[2]) for x in speeches]
        nonempty=[x for x in speech_text if x]
        repeated=sum(v-1 for v in Counter(nonempty).values() if v>1)
        unique_ratio=len(set(nonempty))/len(nonempty) if nonempty else 0
        scene_positions=list(scene_pattern.finditer(body)); scene_bodies=[body[x.end():scene_positions[j+1].start() if j+1<len(scene_positions) else len(body)] for j,x in enumerate(scene_positions)]
        thin_scenes=sum(1 for t in scene_bodies if han(t)<140 or len(speech_pattern.findall(t))<3)
        dialogue_chars=sum(han(t) for t in speech_text)
        action_text=speech_pattern.sub('',body)
        # Hard incomplete-artifact markers. These are not dramatic ambiguity;
        # they explicitly state that dialogue/action is unwritten.
        placeholders = re.findall(
            r'(?:对白待补|台词待补|此处(?:略写|省略|待写|待补)|后续(?:展开|补写)|\[待补[^]\n]*\]|\bTBD\b|\bTODO\b)',
            body, flags=re.I)
        # conservative flags only; explicit heuristic not an artistic judgement
        flags=[]
        if placeholders:flags.append('UNWRITTEN_PLACEHOLDER_BLOCKER')
        if repeated>=3 or (len(nonempty)>=10 and unique_ratio<.8):flags.append('REPETITIVE_DIALOGUE_REVIEW')
        if scene_bodies and thin_scenes>len(scene_bodies)//2:flags.append('THIN_SCENE_MAJORITY')
        if len(nonempty)>=12 and dialogue_chars/len(nonempty)<14:flags.append('VERY_SHORT_DIALOGUE_AVG')
        if han(action_text)<100:flags.append('INSUFFICIENT_ACTION_TEXT_REVIEW')
        if len(nonempty)>=12 and max(Counter((n or plain) for n,plain,_ in speeches).values(),default=0)/len(nonempty)>.85:flags.append('ONE_VOICE_DOMINATES')
        # Shared long phrase / templated variation detection; flags review only, not bad writing by itself.
        if len(nonempty)>=10:
            def shingles(t, n=9):
                t=re.sub(r'[，。！？、：:\s]','',t)
                return set(t[i:i+n] for i in range(max(0,len(t)-n+1)))
            grams=[shingles(x) for x in nonempty]
            related=0
            for ix in range(len(grams)):
                for jx in range(ix+1,len(grams)):
                    a,b=grams[ix],grams[jx]
                    if a and b and len(a&b)/min(len(a),len(b))>=.55: related+=1
            if related>=max(6,len(nonempty)//2): flags.append('TEMPLATED_DIALOGUE_REVIEW')
        if len(scene_bodies)>=3:
            # Very similar scene prose over repeated locations can suggest no episodic state movement.
            descriptions=[speech_pattern.sub('',t) for t in scene_bodies]
            def chargrams(t,n=6):
                t=re.sub(r'\s+','',t)
                return set(t[i:i+n] for i in range(max(len(t)-n+1,0)))
            forms=[chargrams(x) for x in descriptions]
            near=sum(1 for a in range(len(forms)) for b in range(a+1,len(forms)) if forms[a] and forms[b] and len(forms[a]&forms[b])/min(len(forms[a]),len(forms[b]))>.7)
            if near>=2: flags.append('REPEATED_SCENE_ACTION_REVIEW')
        # Flag only strong textual evidence of no decisions/no change across multiple scenes.
        # This is a REVIEW alert, never a claim to have understood story semantics.
        if len(scene_bodies)>=3 and len(nonempty)>=12:
            no_change=re.findall(r'(?:没有|未曾|始终没有|仍未|不做)(?:\S{0,8})(?:决定|变化|行动|离开|推进|进展|结论|投票|通知)',body)
            debate=len(re.findall(r'讨论|考虑|意见|观点|研究|沟通|商量',body))
            action_hits=len(re.findall(r'冲出去|夺下|击退|打开|摔碎|跑向|救出|带走|撬开|签下|承认|交出|关上|按下|砸开',action_text))
            if len(no_change)>=3 and debate>=12 and action_hits<=2:
                flags.append('STATIC_DEBATE_NO_STATE_CHANGE_REVIEW')
        result.append({'episode':int(m.group(1)),'scenes':len(scene_bodies),'repeat_count':repeated,'unique_dialogue_ratio':round(unique_ratio,3),'thin_scenes':thin_scenes,'unwritten_placeholders':len(placeholders),'dialogue_average_han':round(dialogue_chars/max(len(nonempty),1),1),'adversarial_flags':flags})
    return {'file':str(path),'episodes':result,'note':'Adversarial screening only. No semantic or timed performance guarantee.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('files',nargs='+');parser.add_argument('--output'); args=parser.parse_args()
    data={'files':[inspect(x) for x in args.files]}; result=json.dumps(data,indent=2,ensure_ascii=False)
    if args.output:Path(args.output).write_text(result)
    print(result)
