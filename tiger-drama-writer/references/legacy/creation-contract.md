# 创作合同与证据台账

在写场景前用简洁合同明确故事承诺；完成后用有源文依据的台账检查实际结果。单集创作只设单集合同。不得擅自创作整季。

以下 Schema 保存因果合同，不是完整戏剧大纲。应按 [pacing-payoffs.md](pacing-payoffs.md) 中的说明，用一份人类可读大纲记录观众期待、高潮位置、情绪兑现和场景节拍，并关联相应集数及待兑现事项；不要自行增加强制 JSON 字段，也不要把预检当成戏剧设计验证。

## 合同结构

```json
{
  "workflow_revision": "4.1",
  "mode": "single",
  "scope_basis": {
    "count_source": "inferred",
    "episode_count_reason": "一轮有争议的交涉解决了局部故事，不把答案拖到后面。",
    "merge_review": "到场和第一次失败放在同一场；调整提议及其后果组成第二场。"
  },
  "audience_promise": "新手通过家人协作，赢得一次范围明确的技能胜利。",
  "main_engine": "想显得能干的需要，与公开学习发生冲突。",
  "protagonist_strategy": "观察一次失败，改变一个动作，然后独立测试。",
  "ending_payoff": "新手独立完成任务，并接受导师的能力边界。",
  "endpoint_kind": "skill_independence",
  "target_seconds": [90, 150],
  "episodes": [{
    "number": 1,
    "attempt": "在客人到来前录好一段干净利落的演示。",
    "counteraction": "搭档拒绝伪装新手已经掌握了技能。",
    "choice": "保留失败的尝试，独立测试修正后的做法。",
    "payoff": "不让一只手伸进画面帮忙，独立完成实际操作。",
    "cost": "失去精心准备的开场，并让客人看到失败过程。",
    "mainline_change": "从假装教别人，转变为真正掌握一项可演示的入门技能。",
    "mechanism": "在无人协助下进行实际测试。",
    "next_trigger": "客人提出需要更高难度操作的请求。",
    "scene_budgets": [
      {"scene": 1, "speech_seconds": 38, "independent_action_seconds": 18, "pause_seconds": 5, "overlapped_action_seconds": 6},
      {"scene": 2, "speech_seconds": 38, "independent_action_seconds": 24, "pause_seconds": 7, "overlapped_action_seconds": 6}
    ]
  }],
  "payoff_debts": [{"id": "first_skill", "setup_episode": 1, "due_episode": 1, "promised_result": "独立完成"}]
}
```

选择 Schema 模式 `single`、`season`、`retrospective` 或 `review`。工作路由标签 `scoped continuation` 不是 Schema 模式：单集修复用 `single`，连续批量修复用 `season`，并单独记录修订顺序。指定范围内的集 ID 必须为正数、唯一、递增且连续；改写可以从 EP08 开始。`single` 模式恰好包含一集。其他模式遵守用户要求的集数。不要把字段填满误当作创意有吸引力。

新合同独立于 Skill 版本，继续采用 Schema V4.1，并记录 `workflow_revision: "4.1"` 和 `scope_basis`。`count_source` 使用 `user_fixed`、`inferred` 或 `inherited_assumption`。说明实际事件为何需要当前集数，以及考虑过合并哪些相邻准备段落。三场不是最低要求：按需估算。遵守用户固定的集数。旧合同仍可读取；不要把它们改写得仿佛最初就包含新证据。

对于 `user_fixed` 的多集任务，在 `scope_basis` 中原样记录 `requested_episode_count`；预检会将其与计划集数比较。若未明确记录，`single` 模式默认要求一集。这只能检查内部一致性，不能证明助手如实转录了用户要求；不得把助手自行编出的集数重新标为用户固定。

必需字段 `cost` 可以明确写明没有额外损失，以及结果的有限范围。不得为了填写字段而捏造牺牲。`counteraction` 可以是非人格化阻力（测试失败、物理限制或信息缺口），不一定是另一个人拒绝配合。

用户要求独立结局或季终时，`next_trigger` 可以描述明确解决后的状态，并明确说明不打算设置续集钩子。不要只为填写字段而新增谜团。

提供 `target_seconds` 时，预检要求每集都有按顺序排列的 `scene_budgets`。计划时长 = 对白 + 独立动作 + 停顿；与对白重叠的动作已包含在对白时长中，不得超过对白时长。两场示例总计130秒，只是作者假设。审查会检查实际场次数量，以及中文对白是否被强迫超过每分钟300字。它无法证实实际创作顺序、重叠是否合理或真实演出时长。保留真实顺序；不得事后伪造预算。

终点类型是编辑标签，不是固定的类型学分类。区分 `audience_business`、`content_service`、`skill_independence`、`relationship_shift` 等类型。不匹配只是提示要检查是否发生了偷换，不能直接证明失败。

## 台账结构

```json
{
  "episodes": [{
    "number": 1,
    "sha256": "实际文件的 SHA-256",
    "day": 9,
    "day_quote": "返乡第9日",
    "mechanism": {
      "obstacle": "新手无法复现操作步骤",
      "tactic": "独立测试并补上缺失步骤",
      "outcome": "客户接受教程",
      "quote": "本集至少八个字符的一段唯一准确原文"
    },
    "outcome_kind": "content_service",
    "outcome_quote": "至少八个字符的一段唯一准确结果原文"
  }],
  "time_links": [{
    "source_episode": 1,
    "target_episode": 2,
    "offset_days": 1,
    "quote": "包含明天、次日或后天的唯一准确源文"
  }]
}
```

以上示意用哈希/引文只是文档示例，不可作为实际证据。必须填入真实来源数据。每个受审剧集都要有对应台账行；一份台账绑定一个源文件中的一集。缺失、重复、多余或过期行都会被拒绝。机制和结果字段为可选项，但省略后会保持未评估；若提供，须填写全部必需子字段并使用实际证据。

对于不按天数推进的故事，省略 `day` 和 `day_quote`。时间链接要求两集中都有锚点：包含明确 `第N日/天` 且与填写天数相符的唯一片段。小型确定性检查器只支持“次日”和“后天”表述；日历、具体时刻、改期、谎言、疑问句及其他相对时间表达都应人工检查。不得伪造改期证据来掩盖矛盾。

机制引文只能证明来源；是否支持相应标签由编辑判断。实质相同的场景即使对白不同，也应使用等价的阻碍/策略/结果标签。三个签名匹配会触发复审；有意重复的母题可以保留，但要说明理由。不得为了规避提示而更改标签名称。

检查结尾时，将实际结果类型和原文与合同终点比较。还要人工检查中途的主线变化和未兑现事项。客户委托不能证明已有粉丝收入；一张收据不能证明谜团已经解决；一句认错不能证明行为已经改变。

用人类可读的表格维护待兑现事项、人物知识、道具和资源余额。只有确有需要时才使用复杂连续性工具。Schema 校验无法判断计划是否合理，也无法证明引文所述属实。

## 诊断后的场景处置

For thin/sparse scene cues add `scene_dispositions` at the top level of the same source-bound ledger:

```json
{"scene_dispositions": [{
  "episode": 1, "scene": 2, "decision": "retain",
  "quote": "an exact unique quote within that scene, at least eight characters",
  "assessment": "Name the attempted act, counteraction and consequence that make this short scene sufficient."
}]}
```

使用 `retain`、`rewrite`、`merge` 或 `unresolved`。`retain` 表示判断该场景按现状已足够，不只是因为用户要求保留原稿。如果用户未要求改写，应把已知实质缺陷标为 `unresolved`，并保持原始字节不变。未解决的缺陷会使 `editorial_readiness` 保持待处理；该状态报告文本审查进度，不构成改写授权。改写/合并记录在实际修订稿复核前仍处于待处理；计划修复不等于已经修复。引用同一个场景，不要拿更完整的邻场作为证据。台账中的集哈希也绑定场景处置记录；改动剧本后必须重新审查。编辑也可以记录未被标记场景中的问题。

常规最终审查使用 `--require-scene-review`。即使文本结构清楚，只要处置记录缺失或改动仍待处理，审查就不完整。`source_bound_self_review_only` 仅表示提交的编辑批注覆盖了相关提示；它不是艺术批准，也不是独立评估。绝不要为了获得绿色结果而批量把所有短场景标为保留。
