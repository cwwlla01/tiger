# V2.17 复杂动作与群像协同合同

## 触发条件
出现三人及以上协作、追逐、救援、交接、怪物攻击、连续碰撞或多人同步行动时使用。非复杂镜头不强制填写冗余字段。

## 03 的动作节点最小字段
`beat_id`, `source_anchor`, `actor_ids`, `action`, `target_ids`, `prop_custody_before`, `prop_custody_after`, `screen_direction`, `contact_event`, `observable_end_state`, `knowledge_after`, `take_ids`。每个节点有且仅有一个稳定 `beat_id`；不允许只写“众人混战”。

## 04/05 交接
对每个 beat 保留身份、道具归属、方向、接触和终态。04选择有用的可见关键状态，不要假装静帧覆盖整个动作；05按起点、动作、接触、结果顺序，必要时拆段。交接审计采用结构化 sidecar，不要求在给用户的复制块中塞 JSON。

## 证据分级
结构审计 PASS != 空间可行 PASS != 资产验证 PASS != 成片验收 PASS。缺真实资产时可生成候选提示词但不得冻结生产母版。
