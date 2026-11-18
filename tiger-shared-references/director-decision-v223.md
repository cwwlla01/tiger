# V2.23 导演方案选择与冲突裁决（规范性规则）

## 优先级（高→低）
1. 剧本事实、规则真相、人物认知与批准资产不可变；任何候选触犯则直接否决，不能以分数抵消。
2. 已冻结03导演母版与正式审批；04/05仅继承，不可自行重新选择镜头。
3. 物理空间、动作因果、连续性、可交付性；不确定的模型能力标为 `PILOT_REQUIRED`，不得声称已验证。
4. 场景叙事目的、信息揭示顺序、情绪节奏、人物行动与画面表达。
5. 制作成本与提示词简洁性；不能以低成本牺牲前述门槛。

## 03候选决策记录
仅对存在实质权衡的场景比较2至3个可执行方案，不强迫每镜头多方案。每方案记录 `candidate_id`、`source_anchors`、`scene_goal`、`beat_coverage`、`hard_gate_pass`、`veto_reasons`、`narrative_rationale`、`ai_feasibility`（`SUPPORTED`/`PILOT_REQUIRED`/`UNSUPPORTED`）、`complexity_cost`（1–5）、`tradeoffs`。`selected_candidate_id` 必须指向未否决候选；若无合格方案，输出 `BLOCKED_REVISE` 并交还导演，不可虚构最佳方案。

优先用文字比较叙事效果和代价，不使用伪精确的艺术总分。若两个方案同样满足戏剧目标和硬门槛，才可优先较低复杂度。决策应说明被淘汰方案为什么不如选中方案，并允许 `NO_ALTERNATIVE_NEEDED` 以防冗余设计。

## 04/05交接
04/05必须继承 `decision_id`、`selected_candidate_id`、`source_anchors`、`scene_goal`、`beat_coverage`、`style_version`，并只编译获选镜头；不得把未获选候选混入生成提示词。若03有 `PILOT_REQUIRED`，05保留待试验标记和降级/拆段建议，不得写成已通过。04静帧不承诺时序动作已经实现。

## QA与停止条件
QA仅核对可机读决策合同、来源与批准证据；艺术优劣由独立人工审查。发现硬门槛失败仍获选、决策指向不存在的候选、04/05与03不一致或未知模型能力被宣称支持，应阻断交付。仅在存在明确缺陷时返工，不因微小分数差异反复改镜；同一问题两轮未改善则上报人工决策。
