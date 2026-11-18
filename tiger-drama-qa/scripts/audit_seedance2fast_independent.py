#!/usr/bin/env python3
"""Independent source/continuity cross-check of Seedance2Fast 05 (structural only)."""
import argparse
import json
import re
import sys
from pathlib import Path


def shot_ids(s):
    return [x.upper().replace('-', '').replace('_', '') for x in re.findall(r'SH[-_]?\d{1,4}', s, re.I)]


def audit(file, expected):
    raw = Path(file).read_text(encoding='utf-8')
    errs = []
    take_headers = list(re.finditer(r'^##\s+(T[-\w]+)[｜|\s].*$', raw, re.M))
    all_mapped = []
    if not take_headers:
        errs.append('Q-NO-TAKES: 找不到生成Take')
    for k, m in enumerate(take_headers):
        take = m.group(1)
        body = raw[m.end():take_headers[k + 1].start() if k+1 < len(take_headers) else len(raw)]
        map_match = re.search(r'^\*\*编辑镜头\*\*[：:]\s*(.*)$', body, re.M)
        mapped = shot_ids(map_match.group(1)) if map_match else []
        all_mapped.extend(mapped)
        blocks = re.findall(r'```(?:text|txt)\s*\n(.*?)\n```', body, re.S | re.I)
        if len(blocks) != 1:
            errs.append(take+' Q-COPY-BLOCK: 复制块必须恰好一个')
            continue
        block = blocks[0]
        spans = re.findall(r'【\s*\d{2}:\d{2}(?:\.\d+)?\s*[-–—~至]\s*\d{2}:\d{2}(?:\.\d+)?\s*[｜|]\s*镜头\s*\d+\s*】', block)
        if len(mapped) != len(spans):
            errs.append(take+' Q-SHOT-TIMELINE: 05镜头映射与时间轴条目数不一致')
        if not re.search(r'\*\*合并决策\*\*', body):
            errs.append(take+' Q-MERGE-UNJUSTIFIED: 未审核合并/不合并理由')
        if '【终态】' not in block or '【禁改】' not in block:
            errs.append(take+' Q-END-STATE: 缺终态或禁改约束')
        for field in ('摄影机：', '构图：', '光线：', '动作：', '声音：'):
            if block.count(field) < len(spans):
                errs.append(take+f' Q-PER-SHOT-FIELD: {field}数量少于镜头数')
        if any(t in block for t in ('PLACEHOLDER', '待核验', '@图片1', '见03')):
            errs.append(take+' Q-FAKE-EXECUTION: 复制块包含非模型词或未经证明素材引用')
    exp = shot_ids(expected)
    if not exp:
        errs.append('Q-NO-SOURCE: 必须从03提供expected_shots，不可仅根据05自证来源覆盖')
    else:
        if all_mapped != exp:
            errs.append(f'Q-SOURCE-COVERAGE: 期望{exp}，得到{all_mapped}')
    return {'status': 'INDEPENDENT_STRUCTURE_PASS' if not errs else 'INDEPENDENT_STRUCTURE_FAIL',
            'errors': errs, 'note': '这是与生产脚本分离的静态审查，不能证明导演审美或真实模型视频结果。'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompt', required=True)
    p.add_argument('--expected-shots', required=True)
    a = p.parse_args()
    r = audit(a.prompt, a.expected_shots)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0 if not r['errors'] else 1


if __name__ == '__main__':
    sys.exit(main())
