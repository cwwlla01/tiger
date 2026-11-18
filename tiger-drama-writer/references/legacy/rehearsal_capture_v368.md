# 排练计时采集卡 V3.68

此卡由现场计时员填写；禁止助手自行编造任何实测时间、录音、录像和签名。此卡不能证明录像真实性；最终需要第三方核验。

## 采集规则

1. 先锁定剧本原文及逐节拍计划，分别计算 SHA-256；任何改字必须重新计时。
2. 同一集至少做两个**完整且独立**的 take。每个 take 要有独立 `take_id` 和明确区别的 `evidence_reference`，如视频文件名加 `#take-A@00:00:05-00:02:18`；两次不能共享同一引用。
3. `performed_at` 必须为包含时区的 ISO 8601，如 `2026-10-29T14:30:00+01:00`。计时员在现场填写 `operator`、方法、逐场秒数与转场/停顿秒数；不得从129秒预算抄写。
4. 保留失败、漏台词、漏动作或超时的所有 take，不挑选最漂亮的两次冒充整组均合格。
5. 演员完成全部台词与动作，且确认动作/对白重叠安排的安全性，才可填 `true`。不能证实就填 `false`。
6. 运行 `python scripts/audit_rehearsal.py EP04.md EP04_timing_plan.json rehearsal_log.json --output rehearsal_audit.json`；其 `mechanically_accepted` 仅表示字段逻辑验收，不代表真实排练已由工具独立证明。

## 典型误区

- 同一录像的两个所谓 take 却都填 `evidence_reference: video.mp4`：会被拒绝；必须注明不同的片段/时间码。
- `performed_at: today`、没有时区的时间：会被拒绝。
- 计时在90–150秒但漏读台词、漏做动作：会被拒绝。
- 先填 `status: performed` 再补虚构记录：本地工具无法鉴别虚构，必须保留可独立查验的原始证据并由人核查。
