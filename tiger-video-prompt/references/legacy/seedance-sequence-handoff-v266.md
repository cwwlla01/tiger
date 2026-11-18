# V2.66｜Seedance 2 Fast场次内真实事件顺序和跨Take状态

## 何时使用
用户请求完整Seedance Fast视频提示词且存在可访问的01/03证据时执行。单纯“描述一个人变身”不启动；当前界面具体时长/素材模式未核实时保持TEXT_CANDIDATE，不假装可直接提交。六题固定15秒数据只用于那些专门回归题，不用于新片段。

## 内部计划的新两项合同
1. `sequence_groups` 每组声明 `id`, `event_ids`, `mode: SOURCE_ORDER`。事件引用原V2.65 `critical_events`：需有来源原句、实际复制文本中的唯一动作引文、所属Take；03存在时提供 `director_quote`。一个文档有多个非连续场景时分不同组，不能把整部剧的文字位置机械视为物理时间。多个Take中行动也必须按本组顺序出现；多SH生成Take的事件标明`shot_id`并在对应镜头段出现。
2. 如果真的有两个或更多相邻生成Take，`take_handoffs` 一条对一条：`from_take/to_take/kind`；`CONTINUOUS`边界列出重要状态的 `key/end_value/next_start_value/end_quote/next_quote`，两个实际复制提示词都必须出现明确、唯一的见证句；由 `critical_events[].state_effects` 声明的持续改变必须传递至下段，不能悄悄恢复。真实场景跳转用`SCENE_CHANGE`，需具体理由以及03或01场景依据，不可当成绕过连续性的开关。

## 非线性导演决策
确需打乱**呈现顺序**，将 `mode` 标为 `DIRECTOR_PRESENTATION_REORDER`，在03明写两项及以上事件ID和“先/后/插叙/交叉/倒叙”等次序，并在组内声明 `presentation_event_ids` 与原文确切 `director_order_quote`。这只是结构门禁：还必须由导演及独立QA人工核对是否损害真正物理先后，不自动认定已获审批。

## 运行与边界
`python scripts/audit_seedance_fast_v266.py <plan.json>` 内部会继承V2.65来源哈希和引文、V2.64动态剪辑与V2.63渠道/合并检查，再检查事件先后和跨Take文本状态。运行后仍需人审原剧本→03→05，真实模型/图像/视频证据另行验收。不要把`sequence_groups`、`take_handoffs`和资产审批词塞进用户复制块；用户拿到的仍是完整易用的05提示词。

**跨场次也不自动重置永久状态**：真正换场仍需01或03场景来源；已变蓝的眼睛/头发、永久伤口及持有者持续有效。下一Take画面若出现同一主体，在边界 `properties` 写明前段终态、后段初态与两个文本见证；主体确实不在下一画面时，仅以 `offscreen_keys` 记账并标记不可见状态未验证。不能仅凭SCENE_CHANGE清空状态，返回角色时还要验证真实画面表现。
