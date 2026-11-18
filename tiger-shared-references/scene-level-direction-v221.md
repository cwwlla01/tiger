# V2.21 场景级导演判断合同

## 核心目标
以剧本源锚点为依据，先明确整场戏的 `scene_goal`、`dramatic_question`、`turning_point`、`outcome` 和观众信息变化，再决定镜头数量与结构；禁止为镜头技法而增加镜头。

## 03 场景级契约
每场记录 `scene_id`、`source_anchor`、`scene_goal`、`dramatic_question`、`turning_point`、`outcome`、`scene_beats`（有序 `beat_id`）、`shot_plan`（有序 `shot_id`、`covered_beats`、`function`、`selection_reason`、`duration_intent`、`attention_target`）。
- `function` 取 `ESTABLISH` / `DEVELOP` / `REVEAL` / `REACTION` / `PAYOFF` / `BREATH`。
- `duration_intent` 取 `HOLD` / `NORMAL` / `ACCELERATE`，不是生成时长参数。
- 镜头可以覆盖多个 beat；允许有动机的长镜头、静止镜头、画外信息和留白，不得机械一 beat 一镜。
- 每个镜头的 `selection_reason` 必须说明它如何服务场景目标、信息或情绪变化；无功能镜头应删减或合并。
- `REVEAL` 不得早于源剧本允许的揭示节点；`BREATH` 不得无依据地延长或改变事件顺序。
- 场景内镜头必须覆盖全部必要 `scene_beats`，不可擅自新增剧情事实；结构可检测，审美取舍须人工复核。

## 04/05 编译边界
- 04 仅取该镜头可观察的单帧状态，保留 `scene_id`、`shot_id`、`covered_beats`、`attention_target` 和对应 `function`；不把节奏意图误写为帧内动作。
- 05 保留镜头功能、覆盖节拍、场景内顺序及 `duration_intent`；可提出生成拆段，但不能未经导演批准增删或改排编辑镜头。
- 无法从 03 确定场景级合同，标 `SCENE_CONTRACT_MISSING` 并请求补充，不自行补写。

## 06 审核边界
检查场景目标、节拍覆盖、镜头功能、顺序、04/05 继承；对“是否真正好看”“镜头是否过度设计”出具带证据的人工判断，不以字段通过替代艺术验收。
