#!/usr/bin/env python3
"""V2.59 Seedance 2 Fast 05 deterministic delivery gate.

Checks explicit SH-shot identities inside temporal spans, exact keep ranges, and
POST_ONLY editorial beats. This is a structural / timing check, NOT visual or
semantic QA and NOT a guarantee that any model obeys exact cut timings.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

HEADER = re.compile(r'^##\s+(T[-\w]+|POST\d+)\s*[｜|]\s*(.+)$', re.M)
CODE = re.compile(r'```(?:text|txt)\s*\n(.*?)\n```', re.S | re.I)
SPAN = re.compile(r'【\s*(\d{2}:\d{2}(?:\.\d+)?)\s*[-–—~至]\s*(\d{2}:\d{2}(?:\.\d+)?)\s*[｜|]\s*(SH[-_]?\d{1,4})\s*[｜|]\s*镜头\s*(\d+)\s*】', re.I)
SHOT = re.compile(r'SH[-_]?\d{1,4}', re.I)
FIELDS = ('摄影机：', '构图：', '光线：', '动作：', '声音：')
CUTS = ('硬切', '匹配切', '遮挡转场', '连续运镜', '剪辑：', '溶解', '动作匹配切')


def sec(x: str) -> float:
    a, b = x.strip().split(':', 1)
    return int(a) * 60 + float(b)


def norm(x: str) -> str:
    return re.sub(r'[-_]', '', x.upper())


def shots(x: str | None) -> list[str]:
    return [norm(m.group()) for m in SHOT.finditer(x or '')]


def meta(text: str, name: str) -> str | None:
    m = re.search(r'^\s*\*\*' + re.escape(name) + r'\*\*\s*[:：]\s*(.+?)\s*$', text, re.M)
    return m.group(1).strip() if m else None


def length(v: str | None) -> float | None:
    m = re.search(r'(\d+(?:\.\d+)?)\s*秒', v or '')
    return float(m.group(1)) if m else None


def keep_range(v: str | None) -> tuple[float, float] | None:
    m = re.fullmatch(r'\s*(\d{2}:\d{2}(?:\.\d+)?)\s*[-–—~至]\s*(\d{2}:\d{2}(?:\.\d+)?)\s*', v or '')
    return (sec(m.group(1)), sec(m.group(2))) if m else None


def audit(path: str | Path, expected: str | None = None) -> dict:
    raw = Path(path).read_text(encoding='utf-8')
    matches = list(HEADER.finditer(raw))
    top = raw[:matches[0].start()] if matches else raw
    errors: list[str] = []
    units: list[dict] = []
    source_order: list[str] = []
    if not re.fullmatch(r'Seedance\s*2(?:\.0)?\s*Fast', meta(top, '模型') or '', re.I):
        errors.append('E-MODEL: 未写明 Seedance 2 Fast')
    if not matches:
        errors.append('E-UNITS: 缺少生成Take或POST_ONLY单元')
    if not expected or not shots(expected):
        errors.append('E-SOURCE: 必须传入来自独立导演母版的expected-shots')
    labels = [m.group(1) for m in matches]
    if len(labels) != len(set(labels)):
        errors.append('E-UNIT-DUP: Take或POST ID重复')
    generated_sum = retained_sum = post_sum = 0.0
    for i, h in enumerate(matches):
        ident = h.group(1)
        body = raw[h.end():matches[i + 1].start() if i + 1 < len(matches) else len(raw)]
        mapped = shots(meta(body, '编辑镜头'))
        source_order += mapped
        def fail(code, msg): errors.append(f'{ident} {code}: {msg}')
        if not mapped:
            fail('E-MAP', '缺少编辑镜头元数据')
        if ident.startswith('POST'):
            pt = length(meta(body, '剪辑时长'))
            if pt is None or pt <= 0:
                fail('E-POST-DURATION', '后期插段必须有正的剪辑时长')
            else:
                post_sum += pt
            if len(mapped) != 1:
                fail('E-POST-SHOT', '每张纯后期镜头卡只对应一个SH源镜头')
            if not meta(body, '后期处理') or not meta(body, '声画规则'):
                fail('E-POST-BRIEF', '纯后期卡需要后期处理与声画规则')
            if CODE.search(body):
                fail('E-POST-CODE', '纯后期任务不得伪装成视频生成复制块')
            units.append({'unit':ident, 'kind':'POST_ONLY', 'mapped_shots':mapped, 'edit_seconds':pt})
            continue
        gen = length(meta(body, '生成时长'))
        retained = length(meta(body, '剪辑保留'))
        k = keep_range(meta(body, '剪辑截取'))
        if gen is None or not 4 <= gen <= 15:
            fail('E-GEN', 'Fast官方API生成时长须在4–15秒内；即梦入口另行核实')
        else:
            generated_sum += gen
        if retained is None or retained <= 0:
            fail('E-RETAIN', '缺少正的剪辑保留时长')
        else:
            retained_sum += retained
        if k is None:
            fail('E-KEEP-RANGE', '必须明确剪辑截取的00:00.0–00:xx.x')
        elif gen is not None and retained is not None:
            if k[0] < 0 or k[1] > gen + .06 or k[1] <= k[0] or abs(k[1]-k[0]-retained) > .06:
                fail('E-KEEP-MISMATCH', '截取范围、生成时长和保留秒数不一致')
        if not meta(body, '合并决策'):
            fail('E-MERGE', '缺少真实合并/保留理由')
        if not meta(body, '输入模式') or not meta(body, '素材状态'):
            fail('E-INPUT', '输入模式与素材状态必须声明')
        blocks = CODE.findall(body)
        if len(blocks) != 1:
            fail('E-CODE', '每段Take必须恰有一个可复制的纯text块')
            units.append({'unit':ident,'kind':'TAKE','mapped_shots':mapped,'span_shots':[]})
            continue
        block = blocks[0]
        for label in ('【全局】','风格：','空间锚点：','光线总规则：','气氛：','【终态】','【禁改】'):
            if label not in block:
                fail('E-GLOBAL', f'缺少{label}')
        for invalid in ('PLACEHOLDER','待核验','见03','尚未上传','参考资产待制作'):
            if invalid in block:
                fail('E-MGMT', f'可复制块含内部词：{invalid}')
        if re.search(r'@图片\s*\d+', block):
            fail('E-FAKE-REF', '默认文本模式不得使用未真实绑定的@图片')
        span_matches = list(SPAN.finditer(block))
        span_ids = [norm(s.group(3)) for s in span_matches]
        if span_ids != mapped:
            fail('E-SHOT-SPAN-MAP', f'镜头ID与分秒时间轴不一致：meta={mapped}, spans={span_ids}')
        if not span_matches:
            fail('E-TIMELINE', '未找到明示SH身份的逐秒镜头时间轴')
        last_end = 0.
        for j, m in enumerate(span_matches):
            start, end = sec(m.group(1)), sec(m.group(2))
            clip = block[m.end():span_matches[j+1].start() if j+1<len(span_matches) else len(block)]
            clip = clip.split('【终态】', 1)[0].split('【禁改】', 1)[0]
            if abs(start-last_end) > .06:
                fail('E-TIME-GAP', f'{span_ids[j]}时间轴不连续：预期{last_end:g}，实际{start:g}')
            if end <= start:
                fail('E-TIME-ORDER', f'{span_ids[j]}非正时段')
            if int(m.group(4)) != j + 1:
                fail('E-SHOT-INDEX', '镜头1、镜头2等序号不连续')
            last_end = end
            if j > 0 and not re.match(r'^\s*(?:硬切|匹配切|遮挡转场|连续运镜|溶解|动作匹配切)\s*[。；:：，,]|^\s*剪辑：', clip):
                fail('E-CUT', f'{span_ids[j]}缺明确切镜或连续转场')
            for label in FIELDS:
                v = re.search(re.escape(label)+r'\s*(\S.{4,}?)\s*(?=(?:摄影机：|构图：|光线：|动作：|声音：|$))', clip, re.S)
                if v is None:
                    fail('E-FIELD', f'{span_ids[j]}缺少有效{label}')
        if gen is not None and span_matches and abs(last_end-gen) > .06:
            fail('E-TIME-END', f'镜头轴到{last_end:g}秒，生成时长为{gen:g}秒')
        # Keep region must cover a meaningful part of each declared shot. A transition
        # after the keep boundary is effectively absent from the delivered film.
        if k and span_matches:
            active_ids = [norm(m.group(3)) for m in span_matches if min(sec(m.group(2)),k[1])-max(sec(m.group(1)),k[0])> .06]
            if active_ids != mapped:
                fail('E-KEEP-DROPS-SHOT', f'截取范围未覆盖全部镜头：{active_ids} vs {mapped}')
        units.append({'unit':ident,'kind':'TAKE','mapped_shots':mapped,'span_shots':span_ids,
                      'generated_seconds':gen,'retained_seconds':retained,'keep_range':k})
    if expected:
        ids = shots(expected)
        if source_order != ids:
            errors.append(f'E-SOURCE-COVERAGE: 预期{ids}，实际{source_order}')
    if len(source_order) != len(set(source_order)):
        errors.append('E-SHOT-DUP: SH被多个单元重复使用')
    scene = length(meta(top, '剪辑总时长'))
    if scene is None:
        errors.append('E-SCENE: 缺少目标剪辑总时长')
    elif abs(retained_sum + post_sum - scene) > .06:
        errors.append(f'E-SCENE-SUM: Take保留{retained_sum:g}+后期{post_sum:g} != 成片{scene:g}秒')
    return {'status':'TEXT_STRUCTURE_PASS' if not errors else 'TEXT_STRUCTURE_FAIL',
            'errors':errors, 'stats':{'unit_count':len(units),'take_count':sum(u['kind']=='TAKE' for u in units),
                                    'shot_count':len(source_order),'generated_seconds':generated_sum,
                                    'retained_seconds':retained_sum,'post_seconds':post_sum,
                                    'final_seconds':retained_sum+post_sum}, 'units':units,
            'evidence':'TEXT_STRUCTURE_ONLY; NOT_SEEDANCE_TESTED'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prompt_md')
    p.add_argument('--expected-shots', required=True)
    p.add_argument('--json-out')
    a = p.parse_args()
    r = audit(a.prompt_md, a.expected_shots)
    s = json.dumps(r,ensure_ascii=False,indent=2)
    print(s)
    if a.json_out:
        Path(a.json_out).write_text(s+'\n',encoding='utf-8')
    return int(r['status'] != 'TEXT_STRUCTURE_PASS')

if __name__ == '__main__': sys.exit(main())
