# V2.26 同源真实文本 A/B 评估门禁

## 核心规则
- 固定同一份真实/原创完整剧本、资产状态、目标模型、任务书与评审标准，保存 SHA256 和时间戳。对照对象必须有独立生成的 baseline 与 candidate 产物，不能将同一份产物复制两份冒充 A/B。
- `SOURCE_ONLY`：仅有剧本；`BASELINE_ONLY`：有一套产物；`PAIRED_TEXT`：两套独立产物且同源可核验；`HUMAN_REVIEWED`：盲审与错误标签可追溯；`MODEL_OBSERVED`：两组真实模型视频与审核证据齐备。
- 单侧文本可以生成审计清单，不能输出提升百分比、胜负或优于旧版的结论。没有实际运行的版本不得标为已运行。
- 先检查来源事件和因果，再检查分镜选择、04/05提示词冗余与QA误报；成本、token、视频成功率只在有真实观测记录时计算。
- 盲审需要两个独立评分者或说明不足；差异分歧保留，不自动以结构指标替代艺术判断。
- 严格遵守权威冻结和职责边界；导演不得擅改剧情，编译器不得重导，QA不得修改母版。

## 交付字段
`case_id`, `source_path`, `source_sha256`, `baseline_version`, `candidate_version`, `baseline_artifacts`, `candidate_artifacts`, `evidence_level`, `comparison_eligible`, `missing_evidence`, `findings`。

## 执行
先运行 `scripts/ab_evidence_v226.py` 校验 A/B 证据；只有 `comparison_eligible=true` 才能调用 V2.25 `benchmark_skill_v225.py` 比较结构指标。未满足条件时仅交付阻断报告，禁止虚构对照结果。
