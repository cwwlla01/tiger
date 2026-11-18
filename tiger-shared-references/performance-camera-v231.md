# V2.31 表演触发摄影机：戏剧意图优先

- 对每个重要表演节拍先确定 `source_beat_id`、人物目标、可观察行为、观众应知信息、情绪转折；**不得**把抽象心理词直接当成可生成动作。
- 镜头选择必须有 `performance_trigger`：视线转向、呼吸变化、手指停顿、身体重心变化、接触、台词反应或有意的无动作。不要规定所有节拍都要特写。
- 记录 `camera_response`（STATIC/MOVE/CUT/HOLD）、`response_timing`（BEFORE/DURING/AFTER/NONE）、`attention_target`、`cut_reason` 和 `exit_state`；运动与切镜都要说明为何优于不动。
- 情绪曲线以可观察行为和信息变化驱动；避免无依据的泪水、颤抖、夸张瞳孔变化、机械推镜。静止和留白允许作为主动设计。
- 人物交互时保留视线方向、轴线、站位、道具持有和因果顺序；对表演反应允许必要的延迟，不把每句台词机械配一个反应镜头。
- `source_beat_id` 是源剧本追溯标识；`DIRECTOR_DESIGN` 只允许合理表演调度，新增剧情事实须 `WRITER_APPROVAL_REQUIRED`。
- 这些字段是**重要表演节点的内部决策记录**，不要求所有普通镜头重复冗长表格；默认仍只交付 03。
