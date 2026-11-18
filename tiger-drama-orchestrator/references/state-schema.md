# 生产状态文件 `00-生产总控状态.json`

最小字段：`schema_version`, `project`, `updated_utc`, `stages`, `authority`, `blockers`, `tickets`, `history`。

每个 stage 包含 `status`（`NOT_STARTED`/`CANDIDATE`/`NOT_VERIFIED`/`BLOCKED`/`APPROVED`）、`artifacts`（路径、存在、sha256）、`owner_skill`、`upstream_hashes`。`APPROVED` 只能来自可追溯的明确授权，扫描工具不得自动设置。

`authority` 保存每个阶段经明确批准的权威文件路径、sha256和批准证据；未指定时为null。`blockers`记录不可继续的具体原因。`tickets`记录06工单状态，06之外不能将其标为CLOSED。`history`记录实际执行及证据，不得记录虚构的Skill调用。

扫描结果仅代表文件存在性及校验和，绝不代表内容正确或权威。`NOT_VERIFIED` 且有文件只能作为待核验候选输入，不会自动升级为 `CANDIDATE` 或 `APPROVED`。

## 计划字段

`plan` 为每个未批准阶段生成只读建议：

- `unresolved_upstream`：缺少可用上游状态或产物，当前不能安全开始候选工作。
- `upstream_review_required`：上游文件存在但仍为 `NOT_VERIFIED`；下游可按明确请求制作候选稿，同时保留核验提示。
- `unapproved_upstream`：尚无明确批准的上游阶段。
- `ready_for_candidate`：依赖足以开始候选制作；不代表内容正确、已验收或可正式生产。
- `ready_for_authoritative_handoff`：适用上游全部为 `APPROVED`。这是保守提示，不替代用户授权或06审核。

当前全流程依赖为 `01 → 02 → 03 → 04/05 → 06`；02 在03前提供本集相关资产身份和造型匹配，03 后仅对新增资产/造型作定向增量。阶段计划不调用任何 Skill，也不自动创建或批准阶段产物。
