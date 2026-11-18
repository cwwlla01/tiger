# V2.19 动作高潮与电影节奏导演规范

## 适用与创作判断
- 仅适用于剧本中有明确危机、行动抉择、反制或高潮的段落。**不强制套用节拍模板**；节奏应服务人物抉择和观众信息，而非机械加速剪辑。
- 在03以源锚点标记 `source_event_ids`，明确 `sequence_id`、`beat_id`、`dramatic_function`（SETUP / ESCALATE / CHOICE / REVERSAL / PAYOFF / AFTERMATH）、`character_goal`、`threat_delta`、`audience_knowledge`、`cost_paid`、`result_evidence`。无源依据的新增结果须 `WRITER_APPROVAL_REQUIRED`。
- 高潮优先选择清楚的因果镜头：建立危险与距离→人物作出选择→动作接触/失败→结果证据→情绪余波。可以用静默、持镜、声音先行、遮挡与反应制造强度，不用全程快速切镜。
- `tempo_intent` 只用 `HOLD` / `BUILD` / `BURST` / `RELEASE` 表示导演节奏意图；镜头时长是建议值，不得声称模型能准确执行。记录 `focus_owner` 和 `attention_transition`，说明观众为何转移关注。
- 每次局势逆转必须记录 `reversal_trigger` 与 `state_before/after`，代价和结果必须可在画面、声音或明确后期中验证。失败不能被自动美化为成功。
- `shot_design` 包括起止构图、轴线、焦距倾向、运动路径、声音边界与可替代方案。不得仅靠炫技运镜代替动作事实。

## 03 交接
按每个节拍输出：`sequence_id,beat_id,source_event_ids,dramatic_function,tempo_intent,focus_owner,attention_transition,threat_delta,reversal_trigger,state_before,state_after,cost_paid,result_evidence`；不适用的字段用 `NONE`，不要猜测。03 为权威版本，04/05 只读继承。