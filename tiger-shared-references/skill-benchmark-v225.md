# V2.25 同题对照评估协议

## 目的与证据分级
- 本版本优化的是 Skill 自身。以**同一份冻结剧本、相同资产状态、同一模型/提示词条件、相同审查口径**对比基线与候选版，不用凭空编写的优秀案例冒充模型实测。
- `FIXTURE_ONLY`：合成数据只证明指标程序能运行；`TEXT_REVIEWED`：人工审阅实际03/04/05；`MODEL_OBSERVED`：已留存真实生成输出与模型信息。不得跨级推断。
- 不允许为取得更高分改变剧本事件、对白、人物知识、规则真相或版本权威。任何 P0 违规直接判定候选版不合格，不以其他指标抵消。

## 评估流程
1. 冻结 `case_id`、剧本 SHA256、资产/模型配置、基线 Skill 版本、候选 Skill 版本及抽样范围；固定随机种子和生成次数（如适用）。
2. 对同一输入分别运行基线/候选，存档原始03、04、05、06及耗时、token/字数、人工审阅记录；缺失的输出标 `NOT_VERIFIED`，不能记作零错误。
3. 每条源节拍分配唯一 `beat_id`，对比节拍覆盖率、无来源新增率、提示词重复率、单位 Take 字数、QA 误报率与漏报率。误报/漏报须有人工金标准，不能由 QA 自己裁定。
4. 使用 `scripts/benchmark_skill_v225.py` 检查输入完整性并计算**描述性指标**；分母为零返回 `NOT_VERIFIED`，不填零。
5. 输出逐案例差异、P0阻断、置信度/样本限制；只有在证据完整且无退化时建议推广，不自动覆盖已安装 Skill。

## 指标定义
- `beat_coverage = matched_source_beats / source_beat_count`，以唯一ID集合计数。
- `unsupported_additions = generated_beat_ids - source_beat_ids`，需人工判定是否导演合法补足。
- `prompt_redundancy = 1 - unique_normalized_prompts / nonempty_prompts`，仅为粗略重复信号，不是艺术质量。
- `mean_prompt_chars = sum(prompt_char_lengths)/nonempty_prompts`，不代表模型 token 数。
- `qa_precision = TP/(TP+FP)`、`qa_recall = TP/(TP+FN)`，须有独立人工金标准；没有就 `NOT_VERIFIED`。
- 运行时长与模型实际表现只能由真实日志/产物提供；不得根据合成 fixture 声称性能提升。
