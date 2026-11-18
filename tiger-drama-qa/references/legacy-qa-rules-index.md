# Tiger Drama QA — 历史版本规则索引

本文件收录 V2.2–V2.57 的历史审核规则。仅在用户明确要求对应历史版本审核、旧格式回归测试或特定案例审计时加载对应 reference 文件。

## 视觉与空间审核（V2.2–V2.7）
- V2.2 视觉QA：[visual-consistency-v22.md](visual-consistency-v22.md)
- V2.3 视觉交接结构化辅助检查：同上，运行 scripts/audit_visual_contract.py
- V2.4 世界坐标布光门禁：[world-lighting-continuity.md](world-lighting-continuity.md)，运行 scripts/audit_world_lighting.py
- V2.5 人物走位与光区穿越：[character-blocking-lighting.md](character-blocking-lighting.md)，运行 scripts/audit_blocking_lighting.py
- V2.6 面部朝向与遮挡检查：[face-orientation-occlusion.md](face-orientation-occlusion.md)
- V2.7 统一视觉状态交接：[unified-visual-handoff.md](unified-visual-handoff.md)

## 流程与修复（V2.10–V2.11, V1–V5）
- V2.10 Skill 优化闭环与停止规则：[skill-improvement-loop.md](skill-improvement-loop.md)
- V2.11 证据化交接与回归门禁：[evidence-handoff-regression.md](evidence-handoff-regression.md)
- V2 多角色会审与自动修复：[roles-and-repair.md](roles-and-repair.md)，运行 scripts/repair_workflow.py
- V3 语义修复候选与独立复验：运行 scripts/semantic_repair.py
- V4 候选修复独立复验门禁：运行 scripts/review_candidates.py
- V5 证据包与下游影响追踪：运行 scripts/trace_repair_impact.py

## 叙事与导演审核（V2.12–V2.24）
- V2.12 叙事导演与艺术质量：[narrative-direction-quality.md](narrative-direction-quality.md)
- V2.13 情绪节奏与悬念揭示：[suspense-rhythm-v213.md](suspense-rhythm-v213.md)
- V2.14 人物表演与微动作编译：[performance-direction-v214.md](performance-direction-v214.md)
- V2.15 多人物对手戏独立审计：[dialogue-power-v215.md](dialogue-power-v215.md)
- V2.16 群像调度与注意力交接：[ensemble-blocking-v216.md](ensemble-blocking-v216.md)
- V2.17 复杂动作因果与协同：[action-ensemble-v217.md](action-ensemble-v217.md)
- V2.18 威胁反制合同：[opponent-agency-v218.md](opponent-agency-v218.md)
- V2.19 高潮动作节奏与结果兑现：[climax-action-payoff-v219.md](climax-action-payoff-v219.md)
- V2.20 跨镜头剪辑与声画连续性：[edit-continuity-v220.md](edit-continuity-v220.md)
- V2.21 场景级导演节奏与镜头选择：[scene-level-direction-v221.md](scene-level-direction-v221.md)
- V2.22 跨场景/跨集导演风格连续性：[cross-scene-style-v222.md](cross-scene-style-v222.md)
- V2.23 导演决策质量与规则冲突治理：[director-decision-v223.md](director-decision-v223.md)
- V2.24 执行路由与规则去重：[execution-routing-v224.md](execution-routing-v224.md)

## 基准与评估（V2.25–V2.35）
- V2.25 同题基准与可证实改进：[skill-benchmark-v225.md](skill-benchmark-v225.md)
- V2.26 真实任务对照证据门禁：[real-task-evidence-v226.md](real-task-evidence-v226.md)
- V2.27 双版本盲测与证据约束：[blind-test-v227.md](blind-test-v227.md)
- V2.28 镜头语言审美判断与可追溯交接：[lens-aesthetic-v228.md](lens-aesthetic-v228.md)
- V2.29 混合导演模式（默认）：[hybrid-directing-v229.md](hybrid-directing-v229.md)
- V2.30 场次级镜头组合与情绪递进：[scene-shot-combo-v230.md](scene-shot-combo-v230.md)
- V2.31 表演与摄影机协同：[performance-camera-sync-v231.md](performance-camera-sync-v231.md)
- V2.32 多人对手戏镜头决策：[ensemble-dialogue-camera-v232.md](ensemble-dialogue-camera-v232.md)
- V2.33 三人对峙双方案审美评估：[triangle-confrontation-v233.md](triangle-confrontation-v233.md)
- V2.34 沉默、揭示与反应兑现：[silence-reveal-reaction-v234.md](silence-reveal-reaction-v234.md)
- V2.35 场次级节奏一致性独立审核：[scene-orchestration-v235.md](scene-orchestration-v235.md)

## 剪辑与时序（V2.36–V2.37）
- V2.36 镜头取舍与剪辑经济：[editorial-selection-v236.md](editorial-selection-v236.md)
- V2.37 情绪张力与镜头时序：[emotional-tempo-v237.md](emotional-tempo-v237.md)

## 场次实测与A/B（V2.38–V2.48）
- V2.38 场次镜头语言优先级与实测门禁：[scene-language-evaluation-v238.md](scene-language-evaluation-v238.md)
- V2.39 场次实测与规则减负：[scene-benchmark-rule-pruning-v239.md](scene-benchmark-rule-pruning-v239.md)
- V2.40 冻结场次对照：[frozen-scene-comparison-v240.md](frozen-scene-comparison-v240.md)
- V2.41 完整场次独立实测：[real-scene-ab-v241.md](real-scene-ab-v241.md)
- V2.42 场次双稿试运行：[scene-pilot-v242.md](scene-pilot-v242.md)
- V2.43 历史版本独立场次对照：[historical-ab-runbook-v243.md](historical-ab-runbook-v243.md)
- V2.44 历史版本实测门禁：[historical-execution-readiness-v244.md](historical-execution-readiness-v244.md)
- V2.45 历史场次独立执行证据：[historical-execution-v245.md](historical-execution-v245.md)
- V2.46 冻结场次实际产物与来源边界：[frozen-scene-working-draft-v246.md](frozen-scene-working-draft-v246.md)
- V2.47 完整场次导演复审与缺陷修复：[working-scene-director-review-v247.md](working-scene-director-review-v247.md)
- V2.48 PILOT-242 执行交接：[pilot-242-handoff-v248.md](pilot-242-handoff-v248.md)

## 视觉首帧与模式路由（V2.49–V2.50）
- V2.49 视觉首帧门禁：[visual-first-frame-v249.md](visual-first-frame-v249.md)
- V2.50 逐镜头视频生成模式路由：[shot-mode-routing-v250.md](shot-mode-routing-v250.md)

## 专项审查（V2.51–V2.57）
- V2.51 金光式叙事与摄影冲突：[jinguang-camera-qa-v251.md](jinguang-camera-qa-v251.md)
- V2.52 双方案证据分级：[jinguang-benchmark-review-v252.md](jinguang-benchmark-review-v252.md)
- V2.53 原创测试剧本实编与证据边界：[actual-script-practice-v253.md](actual-script-practice-v253.md)
- V2.54 导演复审 QA：[director-review-qa-v254.md](director-review-qa-v254.md)
- V2.55 物理接触走位闭环：对应 V2.55 参考文件
- V2.56 局部可执行生产：[v256-partial-production.md](v256-partial-production.md)
- V2.57 非实机收尾：[preproduction-closure-v257.md](preproduction-closure-v257.md)

## 通用原则
- 所有历史规则中的"文本/清单通过（PASS）不能证明影片质量或实际渠道行为"原则始终有效。
- 不得将静态检查称为艺术或真实视频验收。
- 示范草案不能冒充历史版本真实 A/B。
- 不得将同环境编写的两稿称为独立盲测。
- 工作草稿不得冒充历史 Skill 独立运行。
