#!/usr/bin/env python3
"""Static Take/prompt coverage, any Jimeng model; not capability or video QA."""
import argparse
import re
from pathlib import Path

def check(text, model=None):
    ids = set(re.findall(r'(?m)^\s*(?:[-*]\s*)?(?:\*\*)?take_id(?:\*\*)?\s*[:：]\s*([A-Za-z0-9_-]+)', text, re.I))
    if not ids:
        ids = set(re.findall(r'(?m)^#{2,5}\s*(?:Take|TAKE)\s*[:：#-]?\s*([A-Za-z0-9_-]+)', text))
    if not ids:
        ids = set(re.findall(r'(?m)^###\s+(T-\d{3})｜', text))
    heads = re.findall(r'(?m)^(?:#{3,5}\s*|-\s*\*\*)视频生成提示词[｜|]\s*即梦\s+(.+?)\s*（主用）(?:\*\*：)?\s*$', text)
    post_only = len(re.findall(r'(?m)^- \*\*视频生成处理\*\*：黑场与声音属于后期', text))
    if model is not None:
        heads = [h for h in heads if h.strip() == model.strip()]
    errors=[]
    if not ids: errors.append('未发现可识别的 take_id')
    if not heads: errors.append('未发现目标即梦模型主提示词段落')
    if ids and len(heads) + post_only != len(ids): errors.append(f'Take 数量 {len(ids)} 与主提示词数量 {len(heads)} + 后期专用 {post_only} 不一致（启发式统计）')
    return ids, heads, errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument('storyboard', type=Path)
    p.add_argument('--model', help='指定即梦主模型显示名；不填则统计所有即梦主提示词')
    a=p.parse_args()
    ids,heads,errors=check(a.storyboard.read_text(encoding='utf-8'), a.model)
    print(f'Takes={len(ids)}; Jimeng_main_prompts={len(heads)}; model={a.model or "any"}')
    for e in errors: print('CHECK:',e)
    if errors: raise SystemExit(1)
    print('STATIC PASS (not model capability, image, or video QA)')

if __name__=='__main__': main()
