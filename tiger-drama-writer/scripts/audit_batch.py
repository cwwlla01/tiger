#!/usr/bin/env python3
"""
tiger-drama-writer｜多集 / 阶段批次体检脚本（自给自足，零 Token 预处理）
用于写满 5～10 集或一个剧情阶段后，一键生成轻量阶段审计包：
1) 批量执行每集确定性硬校验（场次、动作行、纯口播字数与代理时长、镜头违禁词、旁注渗漏、死人开口）
2) 串联多集 state_capsule.json：检查人物生死/退场闭环、伤势与服装/道具变更轨迹
3) 统计伏笔债务台账（payoff_debts）：标出已兑现、超期未还（OVERDUE）与长期悬置（STALE）钩子
4) 抽取相邻集“上集末场 ↔ 下集首场”接缝对照文本，供模型低成本做宏观连续性与节奏复核
"""
import argparse
import glob
import json
import os
import re
import sys
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from lint_script import AUTHOR_LEAK_TERMS, FORBIDDEN_TECH_TERMS  # noqa: E402


def natural_ep_key(path: str) -> tuple[int, str]:
    base = os.path.basename(path)
    m = re.search(r"EP0*(\d+)", base, re.IGNORECASE)
    if m:
        return (int(m.group(1)), base)
    m2 = re.search(r"(\d+)", base)
    return (int(m2.group(1)) if m2 else 999999, base)


def parse_ep_num(ep_str: str) -> int | None:
    m = re.search(r"EP0*(\d+)", str(ep_str), re.IGNORECASE)
    return int(m.group(1)) if m else None


def extract_ep_id(path: str, text: str) -> str:
    m = re.search(r"(EP\d{1,4})", os.path.basename(path), re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m2 = re.search(r"^##\s*(EP\d{1,4})\b", text, re.MULTILINE | re.IGNORECASE)
    if m2:
        return m2.group(1).upper()
    return os.path.splitext(os.path.basename(path))[0]


def lint_one(path: str, dead_chars: set[str]) -> dict[str, Any]:
    text = open(path, "r", encoding="utf-8", errors="replace").read()
    lines = text.splitlines()

    scenes: list[tuple[int, str]] = []
    action_lines = 0
    dialogues: list[tuple[int, str, int]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    for idx, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("## "):
            scenes.append((idx, s))
        if s.startswith("△"):
            action_lines += 1

        if "：" in s and not s.startswith("#") and not s.startswith("[") and not s.startswith("△"):
            speaker, content = s.split("：", 1)
            speaker_clean = re.sub(r"（.*?）|\(.*?\)", "", speaker).strip()
            spoken = re.sub(r"（.*?）|\(.*?\)", "", content)
            spoken_chars = len(re.findall(r"[\u4e00-\u9fff]", spoken))
            dialogues.append((idx, speaker_clean, spoken_chars))
            if speaker_clean in dead_chars:
                blockers.append(f"L{idx} [DEAD_CHARACTER_SPEAKS] 已死亡角色 `{speaker_clean}` 出现台词（若为倒叙/闪回请忽略或标注）")

        for term in FORBIDDEN_TECH_TERMS:
            if term in s:
                blockers.append(f"L{idx} [CAMERA_SPEC_LEAK] `{term}`")

        for leak in AUTHOR_LEAK_TERMS:
            if leak in s:
                warnings.append(f"L{idx} [AUTHOR_NOTE_LEAK] `{leak}`")

    if not scenes:
        warnings.append("未检测到标准场头行（`## ...`）")

    total_spoken = sum(c for _, _, c in dialogues)
    if total_spoken < 60:
        warnings.append(f"纯口播字数偏少（{total_spoken} 字），检查是否用动作概括代替了台词交锋")

    return {
        "ep_id": extract_ep_id(path, text),
        "path": path,
        "text": text,
        "lines": lines,
        "scenes": scenes,
        "action_lines": action_lines,
        "dialogue_lines": len(dialogues),
        "spoken_chars": total_spoken,
        "dlg_min_sec": round(total_spoken / 5.0, 1),
        "dlg_max_sec": round(total_spoken / 3.0, 1),
        "blockers": blockers,
        "warnings": warnings,
    }


def extract_first_and_last_scene(lines: list[str], scenes: list[tuple[int, str]], max_lines: int = 35) -> tuple[str, str]:
    if not scenes:
        head = "\n".join(lines[:max_lines]).strip()
        tail = "\n".join(lines[-max_lines:]).strip()
        return head, tail

    first_start = scenes[0][0] - 1
    first_end = scenes[1][0] - 1 if len(scenes) > 1 else len(lines)
    first_block = [l for l in lines[first_start:first_end] if l.strip()]

    last_start = scenes[-1][0] - 1
    last_block = [l for l in lines[last_start:] if l.strip()]

    if len(first_block) > max_lines:
        first_block = first_block[:max_lines] + ["...（首场后续省略）"]
    if len(last_block) > max_lines:
        last_block = [last_block[0], "...（末场前段省略）"] + last_block[-(max_lines - 1):]

    return "\n".join(first_block), "\n".join(last_block)


def resolve_inputs(items: list[str], directory: str, pattern: str) -> list[str]:
    paths: list[str] = []
    for item in items:
        matched = glob.glob(item)
        paths.extend(matched if matched else [item])
    if directory:
        paths.extend(glob.glob(os.path.join(directory, pattern)))
    uniq = sorted({os.path.abspath(p) for p in paths if os.path.isfile(p)}, key=natural_ep_key)
    return uniq


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch audit scripts and state capsules for tiger-drama-writer")
    parser.add_argument("--scripts", nargs="*", default=[], help="Ordered episode script markdown paths or globs")
    parser.add_argument("--scripts-dir", default="", help="Directory containing episode scripts")
    parser.add_argument("--scripts-glob", default="*.md", help="Filename pattern under --scripts-dir (default: *.md)")
    parser.add_argument("--capsules", nargs="*", default=[], help="Ordered state_capsule.json paths or globs")
    parser.add_argument("--capsules-dir", default="", help="Directory containing state capsules")
    parser.add_argument("--capsules-glob", default="*capsule*.json", help="Filename pattern under --capsules-dir")
    parser.add_argument("--stale-after", type=int, default=5, help="Flag unresolved payoff debts open for >= N episodes")
    parser.add_argument("--out", default="", help="Optional path to write compact markdown batch audit packet")
    args = parser.parse_args()

    script_paths = resolve_inputs(args.scripts, args.scripts_dir, args.scripts_glob)
    capsule_paths = resolve_inputs(args.capsules, args.capsules_dir, args.capsules_glob)

    if not script_paths and not capsule_paths:
        print("ERROR: Please provide --scripts / --scripts-dir or --capsules / --capsules-dir.", file=sys.stderr)
        sys.exit(2)

    capsules: list[dict[str, Any]] = []
    for cp in capsule_paths:
        cap = json.load(open(cp, "r", encoding="utf-8"))
        cap["_file"] = cp
        capsules.append(cap)

    # Map episode_id -> capsule, plus index order
    cap_by_ep: dict[str, dict[str, Any]] = {}
    for idx, cap in enumerate(capsules):
        ep_id = str(cap.get("episode_completed") or f"CAP{idx+1:03d}").upper()
        cap_by_ep[ep_id] = cap

    # Lint scripts using previous episode's dead cast when capsules align
    lint_reports: list[dict[str, Any]] = []
    prev_dead: set[str] = set()
    for idx, sp in enumerate(script_paths):
        ep_guess = extract_ep_id(sp, open(sp, "r", encoding="utf-8", errors="replace").read(400))
        ep_num = parse_ep_num(ep_guess)
        # Look up preceding capsule if possible
        dead_for_this: set[str] = set(prev_dead)
        if ep_num is not None and ep_num > 1:
            prev_key = f"EP{ep_num-1:03d}"
            alt_key = f"EP{ep_num-1:02d}"
            prev_cap = cap_by_ep.get(prev_key) or cap_by_ep.get(alt_key)
            if prev_cap:
                dead_for_this = {
                    name
                    for name, info in prev_cap.get("characters", {}).items()
                    if isinstance(info, dict) and "DEAD" in str(info.get("status", "")).upper()
                }
        rep = lint_one(sp, dead_for_this)
        lint_reports.append(rep)

        # Update fallback dead set from this episode's capsule if present
        cur_cap = cap_by_ep.get(rep["ep_id"])
        if cur_cap:
            prev_dead = {
                name
                for name, info in cur_cap.get("characters", {}).items()
                if isinstance(info, dict) and "DEAD" in str(info.get("status", "")).upper()
            }

    # Analyze capsules across batch
    cast_anomalies: list[str] = []
    cast_history: dict[str, list[tuple[str, str, str]]] = {}
    prev_chars: dict[str, dict[str, Any]] = {}
    prop_diffs: list[str] = []
    prev_props: dict[str, str] = {}
    debt_tracker: dict[str, dict[str, Any]] = {}
    prev_open_ids: set[str] = set()

    for step_idx, cap in enumerate(capsules):
        ep_id = str(cap.get("episode_completed") or f"CAP{step_idx+1:03d}").upper()
        ep_num = parse_ep_num(ep_id) or (step_idx + 1)
        chars = cap.get("characters", {})

        # Cast continuity checks
        for name, info in chars.items():
            if not isinstance(info, dict):
                continue
            status = str(info.get("status", "")).strip()
            loc = str(info.get("location", "")).strip()
            cast_history.setdefault(name, []).append((ep_id, status, loc))

            if name in prev_chars:
                p_status = str(prev_chars[name].get("status", "")).upper()
                c_status = status.upper()
                if "DEAD" in p_status and "DEAD" not in c_status and "ALIVE" in c_status:
                    cast_anomalies.append(f"[RESURRECTION_OR_FLASHBACK] `{name}` 在 {ep_id} 从 DEAD 变为 `{status}`")
                p_app = str(prev_chars[name].get("appearance", ""))
                c_app = str(info.get("appearance", ""))
                p_inj = str(prev_chars[name].get("injuries_and_marks", ""))
                c_inj = str(info.get("injuries_and_marks", ""))
                if c_app and p_app and c_app != p_app:
                    prop_diffs.append(f"- {ep_id} 人物外观变化 `{name}`：{p_app} -> {c_app}")
                if c_inj and p_inj and c_inj != p_inj:
                    prop_diffs.append(f"- {ep_id} 伤势/代价变化 `{name}`：{p_inj} -> {c_inj}")

        for p_name, p_info in prev_chars.items():
            p_status = str(p_info.get("status", "")).upper() if isinstance(p_info, dict) else ""
            if "ALIVE" in p_status and p_name not in chars:
                cast_anomalies.append(f"[MISSING_FROM_CAPSULE] 上集存活角色 `{p_name}` 未在 {ep_id} 胶囊中交待去向")

        prev_chars = {k: v for k, v in chars.items() if isinstance(v, dict)}

        # Props diff
        props = {str(k): str(v) for k, v in cap.get("props_and_resources", {}).items()}
        for pk, pv in props.items():
            if pk not in prev_props:
                prop_diffs.append(f"- {ep_id} 新增道具/资源 `{pk}`：{pv}")
            elif prev_props[pk] != pv:
                prop_diffs.append(f"- {ep_id} 道具/资源变化 `{pk}`：{prev_props[pk]} -> {pv}")
        for pk in prev_props:
            if pk not in props:
                prop_diffs.append(f"- {ep_id} 道具/资源移出账本 `{pk}`（请确认是否已消耗或遗失）")
        prev_props = props

        # Payoff debts tracking
        cur_open_ids: set[str] = set()
        for debt in cap.get("payoff_debts", []):
            if not isinstance(debt, dict):
                continue
            did = str(debt.get("id", "")).strip()
            if not did:
                continue
            cur_open_ids.add(did)
            due_str = str(debt.get("due", "")).strip()
            note = str(debt.get("note", "")).strip()
            if did not in debt_tracker:
                debt_tracker[did] = {
                    "first_ep": ep_id,
                    "first_num": ep_num,
                    "last_ep": ep_id,
                    "last_num": ep_num,
                    "due": due_str,
                    "due_num": parse_ep_num(due_str),
                    "note": note,
                    "status": "OPEN",
                }
            else:
                debt_tracker[did]["last_ep"] = ep_id
                debt_tracker[did]["last_num"] = ep_num
                if due_str:
                    debt_tracker[did]["due"] = due_str
                    debt_tracker[did]["due_num"] = parse_ep_num(due_str)
                if note:
                    debt_tracker[did]["note"] = note
                debt_tracker[did]["status"] = "OPEN"

        for prev_id in prev_open_ids - cur_open_ids:
            if prev_id in debt_tracker and debt_tracker[prev_id]["status"] == "OPEN":
                due_n = debt_tracker[prev_id]["due_num"]
                if due_n is not None and ep_num < due_n:
                    debt_tracker[prev_id]["status"] = f"CLEARED_EARLY@{ep_id}"
                else:
                    debt_tracker[prev_id]["status"] = f"RESOLVED@{ep_id}"
        prev_open_ids = cur_open_ids

    latest_ep_num = parse_ep_num(str(capsules[-1].get("episode_completed", ""))) if capsules else None
    if latest_ep_num is None and capsules:
        latest_ep_num = len(capsules)

    debt_alerts: list[str] = []
    for did, info in debt_tracker.items():
        if info["status"].startswith("CLEARED_EARLY@"):
            debt_alerts.append(f"[EARLY_CLOSE_CHECK] `{did}` 原定 {info['due']} 兑现，但在 `{info['status']}` 已从胶囊移出（确认是提前兑现还是漏抄）")
        elif info["status"] == "OPEN" and latest_ep_num is not None:
            age = latest_ep_num - info["first_num"] + 1
            if info["due_num"] is not None and latest_ep_num > info["due_num"]:
                debt_alerts.append(f"[OVERDUE_DEBT] `{did}` 承诺 {info['due']} 兑现，截至第 {latest_ep_num} 集仍未清偿：{info['note']}")
            elif age >= args.stale_after:
                debt_alerts.append(f"[STALE_DEBT] `{did}` 自 {info['first_ep']} 挂起已达 {age} 集：{info['note']}")

    # Assemble Markdown Batch Audit Packet
    md: list[str] = [
        "# 多集 / 阶段批次体检报告",
        "",
        f"- 检查剧本数：`{len(lint_reports)}` 集 | 串联胶囊数：`{len(capsules)}` 份",
        "",
        "## 1. 逐集确定性硬校验与台词密度",
        "",
        "| 集数 | 场数 | △动作 | 台词句数 | 纯口播字数 | 对白代理时长(180-300字/分) | 硬阻断 | 警告 |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    total_blockers = 0
    for r in lint_reports:
        total_blockers += len(r["blockers"])
        md.append(
            f"| {r['ep_id']} | {len(r['scenes'])} | {r['action_lines']} | {r['dialogue_lines']} "
            f"| {r['spoken_chars']} | {r['dlg_min_sec']}s~{r['dlg_max_sec']}s "
            f"| {len(r['blockers'])} | {len(r['warnings'])} |"
        )

    issue_lines = []
    for r in lint_reports:
        for b in r["blockers"]:
            issue_lines.append(f"- `{r['ep_id']}` BLOCKER: {b}")
        for w in r["warnings"]:
            issue_lines.append(f"- `{r['ep_id']}` WARN: {w}")
    if issue_lines:
        md += ["", "### 硬校验明细", *issue_lines]

    md += ["", "## 2. 跨集人物生死、去向与状态闭环"]
    if cast_anomalies:
        md += ["", "### 连续性异常", *[f"- {a}" for a in cast_anomalies]]
    else:
        md += ["", "- 未发现人物生死反转或凭空失踪异常。"]

    if cast_history:
        md += ["", "### 人物状态轨迹摘要"]
        for name, hist in cast_history.items():
            trail = " → ".join(f"{ep}:{st}" for ep, st, _ in hist)
            md.append(f"- **{name}**：{trail}")

    if prop_diffs:
        md += ["", "## 3. 道具、伤势与服装变更流水", *prop_diffs]

    md += ["", "## 4. 伏笔债务台账（payoff_debts）"]
    if debt_alerts:
        md += ["", "### 超期 / 悬置 / 提前移出核验", *[f"- {a}" for a in debt_alerts]]
    if debt_tracker:
        md += [
            "",
            "| 钩子ID | 首次出现 | 承诺兑现 | 当前状态 | 内容 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for did, info in debt_tracker.items():
            md.append(f"| {did} | {info['first_ep']} | {info['due'] or '-'} | {info['status']} | {info['note']} |")
    else:
        md += ["", "- 胶囊中暂无 `payoff_debts` 记录。"]

    if len(lint_reports) >= 2:
        md += ["", "## 5. 相邻集接缝对照（上集末场 ↔ 下集首场）"]
        extracted = [extract_first_and_last_scene(r["lines"], r["scenes"]) for r in lint_reports]
        for i in range(len(lint_reports) - 1):
            cur_r = lint_reports[i]
            nxt_r = lint_reports[i + 1]
            _, cur_tail = extracted[i]
            nxt_head, _ = extracted[i + 1]
            md += [
                "",
                f"### 接缝：{cur_r['ep_id']} 末场 → {nxt_r['ep_id']} 首场",
                "```text",
                f"【{cur_r['ep_id']} 末场】",
                cur_tail,
                "",
                f"【{nxt_r['ep_id']} 首场】",
                nxt_head,
                "```",
            ]

    report_text = "\n".join(md) + "\n"
    if args.out:
        out_dir = os.path.dirname(os.path.abspath(args.out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report_text)

    status_tag = "BLOCKED" if total_blockers else ("NEEDS_REVIEW" if (cast_anomalies or debt_alerts) else "PASS")
    print(
        f"Batch Audit [{status_tag}] | Scripts: {len(lint_reports)} | Capsules: {len(capsules)} "
        f"| Lint Blockers: {total_blockers} | Cast Anomalies: {len(cast_anomalies)} | Debt Alerts: {len(debt_alerts)}"
    )
    if args.out:
        print(f"Audit packet written to: {args.out}")
    if total_blockers:
        sys.exit(1)


if __name__ == "__main__":
    main()
