#!/usr/bin/env python3
"""Screenplay dialogue-duration *proxy*, never measured rehearsal runtime."""
import argparse
import json
import re
from pathlib import Path
from audit_script_batch import EP, SC, SPEECH, han


def estimate(path, slow_cpm=180, fast_cpm=300, action_seconds_per_scene=(12, 35), *, scene_pattern=SC,
             episode_pattern=EP, speech_pattern=SPEECH, source_text=None):
    if slow_cpm <= 0 or fast_cpm <= 0 or slow_cpm > fast_cpm:
        raise ValueError('Expected positive slow_cpm <= fast_cpm')
    if len(action_seconds_per_scene) != 2 or action_seconds_per_scene[0] < 0 or action_seconds_per_scene[1] < action_seconds_per_scene[0]:
        raise ValueError('Invalid action staging interval')
    source = source_text if source_text is not None else Path(path).read_text(encoding='utf-8')
    headings = list(episode_pattern.finditer(source))
    rows = []
    for i, head in enumerate(headings):
        text = source[head.end():headings[i+1].start() if i+1 < len(headings) else len(source)]
        text = re.split(r'^---\s*\n\s*##\s*(?:附录|验收|审稿|质量|续写|状态|附注)', text, maxsplit=1, flags=re.M)[0]
        lines = speech_pattern.findall(text)
        spoken = sum(han(t) for _, _, t in lines)
        scenes = len(scene_pattern.findall(text))
        minimum = spoken / fast_cpm * 60 + scenes * action_seconds_per_scene[0]
        maximum = spoken / slow_cpm * 60 + scenes * action_seconds_per_scene[1]
        rows.append({'episode':int(head.group(1)),'dialogue_han':spoken,'dialogue_turns':len(lines),'scenes':scenes,
                     'estimated_seconds_range':[round(minimum),round(maximum)],
                     'target_90_150s':'POSSIBLE_NOT_MEASURED' if minimum <= 150 and maximum >= 90 else 'OUTSIDE_PROXY_RANGE_REVIEW',
                     'measured_runtime_seconds':None})
    return {'file':str(path),'assumptions':{'slow_dialogue_han_per_min':slow_cpm,'fast_dialogue_han_per_min':fast_cpm,
           'scene_action_staging_seconds':list(action_seconds_per_scene)},'episodes':rows,
           'warning':'This proxy excludes overlapping speech, physical-action complexity, silent beats, camera editing, and actor delivery. It is NOT timed read-through or measured screen runtime.'}


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--output')
    a=ap.parse_args()
    result=estimate(a.file)
    output=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:Path(a.output).write_text(output,encoding='utf-8')
    print(output)
