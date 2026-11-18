#!/usr/bin/env python3
"""Heuristic screenplay coverage audit. NOT an artistic or runtime certificate."""
import argparse, json, re
from pathlib import Path

EP = re.compile(r'^#{1,2}\s*(?![^\n]*\/\s*SC\s*\d+)[^\n]*?\bEP\s*0*(\d{1,3})(?!\d)(?=[《\s｜|：:—–-]|$)[^\n]*$', re.I | re.M)
SC = re.compile(r'^#{2,4}\s*(?:(?:EP\s*\d+\s*/\s*)?SC\s*\d+|\d+[-.]\d+|场景?[一二三四五六七八九十\d]+(?=[\s｜|：:—–-]|$))[^\n]*$',re.I|re.M)
SPEECH = re.compile(r'^[ \t]*(?:\*\*([^*\n]{1,24})\*\*|([\u3400-\u9fffA-Za-z][\u3400-\u9fffA-Za-z0-9·_-]{0,15}))(?:\([^\n)]*\))?[ \t]*[：:][ \t]*(.+)$',re.M)

def han(t): return len(re.findall(r'[\u3400-\u9fff]',t))
def audit(path, *, scene_pattern=SC, episode_pattern=EP, speech_pattern=SPEECH, source_text=None):
    s=source_text if source_text is not None else Path(path).read_text(encoding='utf-8')
    eps=[m for m in episode_pattern.finditer(s) if not re.search(r"EP\s*\d+\s*[—–-]\s*(?:EP\s*)?\d+",m.group(0),re.I)]; rows=[]
    if not eps:
        return {'file':str(path),'error':'No EP headings found; expected ## EP21《标题》 or ## EP21｜标题','episodes':[]}
    for i,m in enumerate(eps):
        part=s[m.end():eps[i+1].start() if i+1<len(eps) else len(s)]
        # Exclude appended project logs from the episode's measurements.
        part=re.split(r'^---\s*\n\s*##\s*(?:附录|验收|审稿|质量|续写|状态|附注)',part,maxsplit=1,flags=re.M)[0]
        scenes=len(scene_pattern.findall(part)); speech=speech_pattern.findall(part)
        spoken=sum(han(t) for _,_,t in speech)
        episode=int(m.group(1)); unique_speakers=len(set((n or plain).strip() for n,plain,_ in speech))
        flags=[]
        if scenes<3: flags.append('FEW_SCENES')
        if len(speech)<12: flags.append('LOW_DIALOGUE_TURNS')
        if spoken<180: flags.append('LOW_SPOKEN_TEXT')
        if unique_speakers<2: flags.append('LOW_SPEAKER_DIVERSITY')
        if han(part)<900: flags.append('SHORT_TEXT_REVIEW')
        if re.search(r'(待补|略写|此处展开|TODO|待写)',part,re.I): flags.append('PLACEHOLDER')
        rows.append({'episode':episode,'scenes':scenes,'dialogue_turns':len(speech),'speakers':unique_speakers,'dialogue_han':spoken,'body_han':han(part),'heuristic_flags':flags,'status':'REVIEW_REQUIRED' if flags else 'STRUCTURALLY_REVIEWABLE','runtime':'UNTIMED'})
    ids=[r['episode'] for r in rows]
    return {'file':str(path),'episodes':rows,'duplicates':sorted({n for n in ids if ids.count(n)>1}),'missing_between_minmax':sorted(set(range(min(ids),max(ids)+1))-set(ids)),'note':'These flags are screening heuristics, not artistic quality or timed-runtime acceptance.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--output'); a=ap.parse_args()
    data={'files':[audit(f) for f in a.files]}
    rendered=json.dumps(data,ensure_ascii=False,indent=2)
    if a.output: Path(a.output).write_text(rendered,encoding='utf-8')
    print(rendered)
