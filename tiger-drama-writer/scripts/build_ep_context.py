#!/usr/bin/env python3
"""
tiger-drama-writer｜单集轻量上下文切片生成器（通用版）
从任意短剧项目的设定文档目录中，仅抽取当前集所需的：
1) 本集创作节拍目标
2) 上一集滚动状态胶囊（JSON）
3) 本集实际出场人物/关键词的设定与声线切片
4) 过滤未来集数剧透关键词
"""
import argparse
import json
import os


def iter_md_files(docs_dir: str, include_subdirs: list[str]) -> list[str]:
    paths = []
    for sub in include_subdirs:
        target = os.path.join(docs_dir, sub) if sub else docs_dir
        if not os.path.isdir(target):
            continue
        for root, _, files in os.walk(target):
            for fn in sorted(files):
                if fn.endswith(".md"):
                    paths.append(os.path.join(root, fn))
    return sorted(set(paths))


def extract_matching_lines(md_text: str, keywords: list[str], exclude: list[str]) -> list[str]:
    matched = []
    for raw in md_text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if not (s.startswith("|") or s.startswith("- ") or s.startswith("**")):
            continue
        if exclude and any(ex in s for ex in exclude):
            continue
        if any(k in s for k in keywords):
            matched.append(s)
    return matched


def main():
    parser = argparse.ArgumentParser(description="Build compact per-episode context packet for tiger-drama-writer")
    parser.add_argument("--docs-dir", required=True, help="Project docs root directory")
    parser.add_argument("--subdirs", default="world,production", help="Comma-separated subdirs under docs-dir to slice (empty=all)")
    parser.add_argument("--capsule", required=True, help="Path to current rolling state_capsule.json")
    parser.add_argument("--ep", required=True, help="Target episode ID, e.g. EP002")
    parser.add_argument("--cast", required=True, help="Comma-separated cast names for this episode")
    parser.add_argument("--keywords", default="", help="Extra location/monster/prop keywords to slice")
    parser.add_argument("--exclude-keywords", default="", help="Comma-separated future spoiler keywords to exclude")
    parser.add_argument("--beat", required=True, help="Target episode beat/goal summary")
    parser.add_argument("--max-extra-lines", type=int, default=40, help="Cap extracted keyword lines to keep packet compact")
    parser.add_argument("--out", required=True, help="Output markdown packet path")
    args = parser.parse_args()

    subdirs = [s.strip() for s in args.subdirs.split(",")] if args.subdirs.strip() else [""]
    cast_list = [c.strip() for c in args.cast.split(",") if c.strip()]
    kw_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
    excl_list = [x.strip() for x in args.exclude_keywords.split(",") if x.strip()]

    capsule = json.load(open(args.capsule, "r", encoding="utf-8"))
    md_files = iter_md_files(args.docs_dir, subdirs)

    full_bytes = 0
    for root, _, files in os.walk(args.docs_dir):
        for fn in files:
            if fn.endswith(".md"):
                full_bytes += os.path.getsize(os.path.join(root, fn))

    cast_lines = []
    extra_lines = []
    for path in md_files:
        txt = open(path, "r", encoding="utf-8", errors="replace").read()
        cast_lines.extend(extract_matching_lines(txt, cast_list, excl_list))
        if kw_list:
            extra_lines.extend(extract_matching_lines(txt, kw_list, excl_list))

    cast_lines = list(dict.fromkeys(cast_lines))
    extra_lines = [l for l in dict.fromkeys(extra_lines) if l not in cast_lines][: args.max_extra_lines]

    out_lines = [
        f"# {args.ep} 轻量上下文切片包",
        "",
        f"## 1. 本集创作目标（{args.ep}）",
        args.beat,
        "",
        "## 2. 上一集滚动状态胶囊",
        "```json",
        json.dumps(capsule, ensure_ascii=False, indent=2),
        "```",
        "",
        f"## 3. 出场人物设定与声线切片（{', '.join(cast_list)}）",
        *cast_lines,
        "",
    ]

    if extra_lines:
        out_lines += [
            f"## 4. 场地／规则／道具切片（{', '.join(kw_list)}）",
            *extra_lines,
            "",
        ]

    packet = "\n".join(out_lines)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(packet)

    pkt_bytes = len(packet.encode("utf-8"))
    ratio = (1 - pkt_bytes / full_bytes) * 100 if full_bytes else 0
    print(f"Docs total: {full_bytes:,} bytes | Sliced packet: {pkt_bytes:,} bytes | Reduced by {ratio:.1f}%")


if __name__ == "__main__":
    main()
