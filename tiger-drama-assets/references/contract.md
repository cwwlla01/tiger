# 资产总库与导演/生产交接协议 v2

## 执行顺序
- 完整单集流程：01冻结 → 02轻量资产/造型匹配 → 03导演 → 02定向增量（仅有新资产/造型提案或实质冲突时）→ 04/05。
- 02前置只负责查本集涉及资产及其既有设定/造型，给03提供可信的 ID/Look 上下文；不预先替03规定镜头。03只需控制本集如何使用、遮挡、揭示和组织造型。
- 03后只处理新增/变化项，禁止全量重跑02与03。导演只请求03时，可只读查询已存在的资产造型，不强迫生成02文件。

## 数据与权限
- Asset registry owner 分配 canonical `individual_id`、`stage_id`、`look_id`，维护 aliases、source evidence、approval 和 versions。
- 02可在首次入库或明确新造型时创建稳定 ID 与候选记录；候选 ID 不等于设计已批准。
- Director 使用02匹配的造型并提交镜头中的使用/揭示方式；可提出新增 Look/资产需求、`TMP-` 临时 ID、镜头状态、所需视角/帧 ID，不可替资产库批准正式设计或写入 `APPROVED`。
- Producer 返回 `candidate_revision`、实际路径或 Studio slot、真实审图结果；Registry owner 核验并保存。`QC_PASSED` 不能自动升为 `APPROVED`。
- 项目 ID 为命名空间；跨项目不能凭同名自动复用。物种/风格模板可共享，但个体身份不可无证据共享。

## 数据约定
全局人类可读文件默认位于 `全局资产/{人物|道具|场景|怪物}/`：每个资产各有 `<资产名称>-设定.md` 和 `<资产名称>-造型.md`。Asset ID/aliases/身份事实保存在设定文件；Stage/Look ID、故事适用时间、可复用设计与状态保存在造型文件。同名冲突时文件名加稳定ID后缀。现有 Registry JSON 可继续作为索引/兼容数据源；迁移必须由单独任务执行，不能在普通单集解析中擅自重写。

Registry JSON 根（若项目仍使用）：`schema_version`, `project_id`, `history_status`, `individuals`, `conflicts`。
Individual：`individual_id`, `category`, `name`, `aliases`, `identity_notes`, `stages`。
Stage：`stage_id`, `core_traits`, `persona`(人物可选), `looks`。
Look：`look_id`, `design_traits`, `approval_status`, `provenance`, `text_version`, `image_revisions`。
Image revision：`version`, `image_status`, `approval_status`, `uri`, `source_proof`。`uri` 空值不得标为 `IMAGE_VERIFIED`；已验证图像需可访问实际路径/图位和核验记录。
Conflict：`conflict_id`, `individual_id`, `episode_ids`, `left_evidence`, `right_evidence`, `status`, `resolution`。

Handoff 根：`schema_version`, `project_id`, `director_source`, `asset_requirements`, `production_tasks`, `resolved_bindings`。
Requirement：`requirement_id`, `episode_id`, `shot_id`, `take_id`, `frame_ids`, `individual_id`, `stage_id`, `look_id`, `version`, `transient_state`, `required_view`, `priority`, `status`, `provenance`。阶段转换可额外 `transition_to_stage_id`。
Production task：`task_id`, `requirement_ids`, `target_skill`, `action`, `identity_lock`, `shot_constraints`, `status`。
Resolved binding：`requirement_id`, `individual_id`, `stage_id`, `look_id`, `image_revision`, `image_uri`, `verification_status`。

## 状态
- `history_status`: `VERIFIED` / `PARTIAL` / `REGISTRY_UNAVAILABLE` / `HISTORY_NOT_VERIFIED`。
- `approval_status`: `PROPOSED` / `QC_PASSED` / `APPROVED` / `REJECTED` / `CONFLICT`。
- `image_status`: `IMAGE_VERIFIED` / `TEXT_ONLY` / `IMAGE_MISSING` / `UNKNOWN`。
- `priority`: `BLOCKING` / `HIGH` / `NORMAL` / `OPTIONAL`。
- `provenance`: `SCRIPT_EXPLICIT` / `APPROVED_HISTORY` / `ASSET_PROPOSAL` / `UNVERIFIED`。
- 不要将未知状态默认设为已批准。

## 合并与冲突策略
1. 同名：先比较身体/物件/场景身份和剧本时间线；没有证据时保留两个候选。
2. 新剧本与旧批准设定冲突：检查阶段切换、造型变更、时间顺序和别名；仍冲突则阻止正式覆盖并生成冲突卡。
3. 正式批准版本不可原地覆盖；新增 revision，并追踪哪个镜头绑定旧/新版本。
4. 新阶段继承旧造型时记录 `inherited_from`，并明确哪些属性继承、哪些发生变化。
5. 多集处理仅扫描用户指定批次及直接连续性依赖；未批准设计可以作为分镜候选上下文，但不得当正式批准母版。
6. 没有明确新造型时，沿用故事时间线上该集之前最近的有效造型；以剧情/effective date排序，不以文件修改时间排序。

## 示例（示意，不是历史资产）
`CHAR-001/S01/L01` 林渊常态；`CHAR-001/S02/L01` 阿禾接管。两阶段同身体，S02 发色与瞳色改变；仓库服装继承。变身镜头引用 `CHAR-001 S01→S02`，并保持同一脸部身份基础。
