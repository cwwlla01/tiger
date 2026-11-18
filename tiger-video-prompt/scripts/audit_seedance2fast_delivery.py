#!/usr/bin/env python3
"""Deterministic TEXT-level gate for Seedance 2 Fast final prompt Markdown.
Does not validate cinematic quality, Jimeng UI compatibility, asset uploads, or actual video.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TAKE_RE = re.compile(r'^##\s+(T[-\w]+)[｜|\s]', re.M)
BLOCK_RE = re.compile(r'```(?:text|txt)\s*\n(.*?)\n```', re.S | re.I)
SPAN_RE = re.compile(r'【\s*(\d{2}:\d{2}(?:\.\d+)?)\s*[-–—~至]\s*(\d{2}:\d{2}(?:\.\d+)?)\s*[｜|]\s*(镜头\s*\d+)\s*】')
SH_RE = re.compile(r'SH[-_]?\d{1,4}', re.I)
MODEL_RE = re.compile(r'Seedance\s*2(?:\.0)?\s*Fast', re.I)


def seconds(stamp):
    minute, second = stamp.split(':', 1)
    return int(minute) * 60 + float(second)


def metadata(section, key):
    p = re.compile(r'^\s*\*\*' + re.escape(key) + r'\*\*\s*[：:]\s*(.+?)\s*$', re.M)
    m = p.search(section)
    return m.group(1).strip() if m else None


def duration(meta):
    if not meta:
        return None
    m = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*秒', meta)
    return float(m.group(1)) if m else None


def shot_ids(text):
    return [m.upper().replace('_', '').replace('-', '') for m in SH_RE.findall(text or '')]


def audit(path, expected_shots=None):
    content = Path(path).read_text(encoding='utf-8')
    errors, warnings, takes, all_shots = [], [], [], []
    if not MODEL_RE.search(content.split('## T', 1)[0]):
        errors.append('E-MODEL: 文档未标明 Seedance 2 Fast')
    matches = list(TAKE_RE.finditer(content))
    if expected_shots is None:
        errors.append('E-NO-SOURCE: 请从03导演分镜明确提供 --expected-shots，以免05自证镜头完整')
    take_ids = [m.group(1) for m in matches]
    if len(take_ids) != len(set(take_ids)):
        errors.append('E-TAKE-DUPLICATE: 重复Take ID')
    if not matches:
        errors.append('E-NO-TAKES: 未找到 ## T01｜... 的 Take')
    for idx, match in enumerate(matches):
        take_id = match.group(1)
        section = content[match.end(): matches[idx + 1].start() if idx + 1 < len(matches) else len(content)]
        def err(code, detail):
            errors.append(f'{take_id} {code}: {detail}')
        generate = duration(metadata(section, '生成时长'))
        retained = duration(metadata(section, '剪辑保留'))
        mapped = shot_ids(metadata(section, '编辑镜头'))
        decision = metadata(section, '合并决策')
        input_mode = metadata(section, '输入模式')
        assets = metadata(section, '素材状态')
        blocks = BLOCK_RE.findall(section)
        if generate is None:
            err('E-GENERATE', '缺少生成时长')
        elif not (4 <= generate <= 15):
            err('E-MODEL-RANGE', '官方火山方舟 Fast 型号时长为4-15秒（即梦UI仍需核实）')
        if retained is None:
            err('E-RETAIN', '缺少独立的剪辑保留时长')
        elif generate is not None and (retained <= 0 or retained > generate + 0.01):
            err('E-RETAIN-RANGE', '剪辑保留时长必须大于0且不超过生成时长')
        if not mapped:
            err('E-SHOT-MAP', '缺少编辑镜头ID')
        all_shots += mapped
        if decision is None or not any(k in decision for k in ('合并', '单镜', '保留')):
            err('E-MERGE-DECISION', '缺少多镜头合并/保留单镜的理由')
        if not input_mode:
            err('E-INPUT-MODE', '缺少输入模式')
        if not assets:
            err('E-ASSET-STATE', '缺少真实素材状态')
        if len(blocks) != 1:
            err('E-COPY-BLOCK', '每个Take必须恰有一个完整text复制块')
            takes.append({'take_id': take_id, 'mapped_shots': mapped, 'spans': []})
            continue
        block = blocks[0]
        for token in ('【全局】', '风格：', '空间锚点：', '光线总规则：', '气氛：', '【终态】', '【禁改】'):
            if token not in block:
                err('E-GLOBAL', f'复制块缺少 {token}')
        for bogus in ('PLACEHOLDER', '待核验', '见03', '参考资产待制作', '尚未上传'):
            if bogus in block:
                err('E-MANAGEMENT-TEXT', f'复制块混入内部管理词 {bogus}')
        if re.search(r'@图片\s*\d+', block):
            err('E-UNVERIFIED-AT-REF', '禁止在默认纯文本复制块伪造@图片引用')
        spans = list(SPAN_RE.finditer(block))
        if not spans:
            err('E-TIMELINE-MISSING', '未找到包含分秒起止的镜头时间段')
        if mapped and spans and len(mapped) != len(spans):
            err('E-SHOT-COUNT', f'编辑镜头数{len(mapped)}与时间段数{len(spans)}不一致')
        last_end = 0.0
        for j, m in enumerate(spans):
            start, end = seconds(m.group(1)), seconds(m.group(2))
            segment_end = spans[j + 1].start() if j + 1 < len(spans) else len(block)
            segment = block[m.end():segment_end]
            # The final state fields may follow the last segment; harmless for presence checks.
            if abs(start - last_end) > 0.06:
                err('E-TIMELINE-GAP', f'镜头{j+1}起点{start:g}秒未承接上镜末端{last_end:g}秒')
            if end <= start:
                err('E-TIMELINE-ORDER', f'镜头{j+1}结束时间必须大于开始')
            last_end = end
            if f'镜头{j+1}' != re.sub(r'\s+', '', m.group(3)):
                err('E-SHOT-LABEL', '镜头序号不连续')
            for field, code in [('摄影机：', 'E-CAMERA'), ('构图：', 'E-FRAMING'), ('光线：', 'E-LIGHT'), ('动作：', 'E-ACTION'), ('声音：', 'E-SOUND')]:
                if field not in segment:
                    err(code, f'镜头{j+1}缺少{field}')
                else:
                    local = re.search(re.escape(field) + r'\s*([^\n]{0,80})', segment)
                    if not local or len(local.group(1).strip(' ，。；;:')) < 6 or local.group(1).lstrip().startswith(('，', '。', '；', ',', ';')):
                        err(code + '-EMPTY', f'镜头{j+1}的{field}无有效内容')
            if j > 0 and not any(t in segment[:90] for t in ('硬切', '匹配切', '遮挡转场', '连续运镜', '溶解', '剪辑：')):
                err('E-CUT', f'镜头{j+1}缺明确切镜/连续转场')
        if generate is not None and spans and abs(last_end - generate) > 0.06:
            err('E-TIMELINE-TAIL', f'最后镜头到{last_end:g}秒，生成时长却是{generate:g}秒')
        takes.append({'take_id': take_id, 'generated_seconds': generate, 'retained_seconds': retained,
                      'mapped_shots': mapped, 'spans': len(spans)})
    if expected_shots:
        expected = shot_ids(expected_shots)
        missing = [s for s in expected if s not in all_shots]
        extra = [s for s in all_shots if s not in expected]
        if missing:
            errors.append('E-SOURCE-MISSING: ' + ','.join(missing))
        if extra:
            errors.append('E-SOURCE-EXTRA: ' + ','.join(extra))
        if expected != all_shots:
            errors.append('E-SOURCE-ORDER: 源镜头顺序与05映射不完全一致')
    if len(set(all_shots)) != len(all_shots):
        errors.append('E-SHOT-DUPLICATE: 编辑镜头在生成Take中重复映射')
    if matches and all(t.get('retained_seconds') is not None for t in takes):
        total = sum(t['retained_seconds'] for t in takes)
        headline = duration(metadata(content[:matches[0].start()], '剪辑总时长'))
        if headline is not None and abs(total - headline) > .06:
            errors.append(f'E-SCENE-DURATION: 保留时长总和{total:g}秒与目标剪辑{headline:g}秒不一致')
    warnings.append('仅通过静态结构检查；仍需导演语义审核、独立QA、图片/模型UI及真实视频核验。')
    return {'status': 'TEXT_STRUCTURE_PASS' if not errors else 'TEXT_STRUCTURE_FAIL', 'errors': errors,
            'warnings': warnings, 'takes': takes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prompt_md', help='Complete final 05 prompt markdown')
    parser.add_argument('--expected-shots', default=None, help='Comma-separated SH IDs from director source')
    parser.add_argument('--json-out', default=None)
    args = parser.parse_args()
    result = audit(args.prompt_md, args.expected_shots)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    print(out)
    if args.json_out:
        Path(args.json_out).write_text(out + '\n', encoding='utf-8')
    return 0 if result['status'] == 'TEXT_STRUCTURE_PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
