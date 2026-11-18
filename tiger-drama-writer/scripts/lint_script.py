#!/usr/bin/env python3
"""
tiger-drama-writer｜第一层确定性剧本硬校验脚本
检查：
1) 场次结构、△ 动作行与纯口播汉字数 / 代理时长（180–300字/分钟）
2) 越界 03/05 镜头/视频模型术语（运镜、焦段、Seedance 等）
3) 作者规则旁注渗漏（如“没人有空确认”“仅某人可见”等）
4) 结合 state_capsule.json 检查已死亡角色是否“诈尸开口”
"""
import argparse
import json
import re
import sys

FORBIDDEN_TECH_TERMS = [
    "推镜头", "拉镜头", "摇镜头", "移镜头", "跟镜头", "航拍", "运镜",
    "焦段", "首尾帧", "Seedance", "分镜", "机位", "景别",
    "大特写", "中近景", "大远景",
]

AUTHOR_LEAK_TERMS = [
    "没人有空确认", "仅未识别者", "仅某人可见", "回到仓库时", "作者注",
]


def main():
    parser = argparse.ArgumentParser(description="Deterministic screenplay linter for tiger-drama-writer")
    parser.add_argument("script", help="Path to episode screenplay markdown file")
    parser.add_argument("--capsule", default="", help="Optional previous state_capsule.json to check dead cast")
    args = parser.parse_args()

    text = open(args.script, "r", encoding="utf-8").read()
    lines = text.splitlines()

    scenes = []
    action_lines = 0
    dialogues = []
    blockers = []
    warnings = []

    dead_chars = set()
    if args.capsule:
        cap = json.load(open(args.capsule, "r", encoding="utf-8"))
        for name, info in cap.get("characters", {}).items():
            if isinstance(info, dict) and "DEAD" in str(info.get("status", "")).upper():
                dead_chars.add(name)

    for idx, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("## "):
            scenes.append((idx, s))
        if s.startswith("△"):
            action_lines += 1

        # Spoken dialogue detection
        if "：" in s and not s.startswith("#") and not s.startswith("[") and not s.startswith("△"):
            speaker, content = s.split("：", 1)
            speaker_clean = re.sub(r"（.*?）|\(.*?\)", "", speaker).strip()
            spoken = re.sub(r"（.*?）|\(.*?\)", "", content)
            spoken_chars = len(re.findall(r"[\u4e00-\u9fff]", spoken))
            dialogues.append((idx, speaker_clean, spoken_chars))
            if speaker_clean in dead_chars:
                blockers.append(f"L{idx} [DEAD_CHARACTER_SPEAKS] 已死亡角色 `{speaker_clean}` 出现台词")

        # Forbidden 03/05 camera/video terms
        for term in FORBIDDEN_TECH_TERMS:
            if term in s:
                blockers.append(f"L{idx} [CAMERA_SPEC_LEAK] 出现越界镜头/视频术语 `{term}`: {s[:40]}")

        # Author annotation leaks
        for leak in AUTHOR_LEAK_TERMS:
            if leak in s:
                warnings.append(f"L{idx} [AUTHOR_NOTE_LEAK] 疑似作者说明口吻 `{leak}`: {s[:40]}")

    if not scenes:
        warnings.append("未检测到标准场头行（如 `## EP001-SC001 ...` 或 `## EP01 / SC01 ...`）")

    total_spoken = sum(c for _, _, c in dialogues)
    dlg_min_sec = round(total_spoken / 5.0, 1)
    dlg_max_sec = round(total_spoken / 3.0, 1)

    print(f"=== Script Lint Report: {args.script} ===")
    print(f"Scenes: {len(scenes)} | Action lines (△): {action_lines} | Dialogue lines: {len(dialogues)}")
    print(f"Spoken CJK chars: {total_spoken} (Dialogue-only proxy @ 180-300 cpm: {dlg_min_sec}s ~ {dlg_max_sec}s; excludes independent actions)")

    if warnings:
        print("\n[WARNINGS]")
        for w in warnings:
            print(" -", w)
    if blockers:
        print("\n[BLOCKERS]")
        for b in blockers:
            print(" -", b)
        sys.exit(1)

    print("\nPASS: No hard blockers detected.")


if __name__ == "__main__":
    main()
