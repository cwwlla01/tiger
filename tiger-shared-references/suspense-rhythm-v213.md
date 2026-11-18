# V2.13 情绪节奏与悬念信息契约

## 导演决策（03）
- 从源剧本抽取可观察的 `beat_id`、源文锚点、观众此刻已知/未知、人物目标与情绪变化；不要新增剧本没有授权的规则真相。
- 每个关键 beat 明确 `reveal_policy`：`SHOW`（现在揭示）、`WITHHOLD`（暂不揭示）、`REACTION_ONLY`（先给反应）、`AUDIO_ONLY`（声音先行）或 `POST_ONLY`（后期实现）。按剧本因果与知识状态安排；不把悬念等同于永远隐藏。
- 每个 Take 指定 `beat_ids`、`emotional_turn`（前后变化）、`rhythm_function`（建立/蓄压/停顿/释放/余波）、`reveal_policy`、`audience_knows_after` 和 `sound_boundary`。没有情绪变化的过渡镜头可标 `NONE`，不强制表演。
- 关键反应镜头必须明确人物看见/听见的刺激、反应起点和可见表演，不允许凭空知道镜头外秘密。
- 对关键悬念尝试“先反应后揭示”和“先揭示后反应”两种节奏，选择源文支持且更清晰的一种；未选方案不写进最终 03。
- 停顿必须有戏剧任务（等待、犹豫、聆听、抉择），不能为了凑时长机械加秒；声音跨剪辑边界需注明何时可听见。

## 04/05 继承
- 04 只画该帧时刻允许观众看到的信息，不提前泄露 `WITHHOLD` 的威胁真相或下一镜事件。
- 05 按 `beat_ids` 的顺序编译刺激→反应→决策→结果；`AUDIO_ONLY`/`POST_ONLY` 不伪装为模型必须生成的可见画面。任何更改揭示时点、信息归属或声音先后都需退回 03。
- 对每个 Take 记录 `source_beat_ids` 和 `reveal_policy` 于内部结构化清单；复制提示词中只保留可执行的画面/动作/声音描述。

## QA 边界
- 以源文事件为基准核对 beat 覆盖、次序、禁提前揭示、声画边界和人物知识状态。缺少源锚点标 `NOT_VERIFIED`，不猜测剧情。
- `scripts/audit_suspense_contract_v213.py` 只检查结构化清单的覆盖、次序、引用与策略漂移。主观节奏质量仍需独立逐镜评审；结构通过不代表艺术通过或视频通过。
- P0：明确剧本真相被提前泄露、关键结局/规则被篡改。P1：有依据的悬念/反应顺序损坏。P2：可改善但不改变事实的节奏建议。

## 数据最小样式
```json
{"source_beats":[{"id":"B1","anchor":"原剧本段落","must_precede":["B2"]},{"id":"B2","anchor":"原剧本段落","must_precede":[]}],"stages":{"03":[{"take_id":"T1","beat_ids":["B1"],"reveal_policy":"REACTION_ONLY"},{"take_id":"T2","beat_ids":["B2"],"reveal_policy":"SHOW"}],"05":[{"take_id":"T1","beat_ids":["B1"],"reveal_policy":"REACTION_ONLY"},{"take_id":"T2","beat_ids":["B2"],"reveal_policy":"SHOW"}]}}
```
