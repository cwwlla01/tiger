# 本次前向试写的实际顺序与限制

1. 接收前提与单集范围，没有收到旧剧本、预期答案或答题钥匙。用户说“重写”，本次因无旧稿按给定前提新写；未假装继承旧文。
2. 读取已安装Skill SKILL.md，以及 creation-contract、pacing-payoffs、review-policy、promise-and-causality、timing-and-evidence。未预先读旧测试样例来仿答。
3. 在写剧本前，依次写入 prewriting_outline.md 与 story_contract.json；随后执行 preflight，保存 preflight.json，字段与预算算术检查无问题。
4. 一次写入完整 EP01.raw.md，两场一集；原稿冻结。未写季纲、第二集、分镜或视频提示。
5. 对冻结原稿执行首次 review，无ledger，保存 initial_diagnostic.json。该初诊明确语义未评估，且短场未处置。
6. 阅读源文及初诊；只检查相关解析器来核实台词计数与时长代理口径（SC01 46汉字，SC02 112汉字）。未修改解析器或Skill指令。
7. 根任务代理实际读取了大纲与原稿，并提醒保留时长和所选回报范围限制。该阅读属模型协作，不是人类或观众测试，不作为独立盲评。
8. 填写源文SHA-256绑定的 editorial_ledger.json；运行含 --require-scene-review 的正常最终review，保存 review.json；写入 manual_review.md 与本记录。原稿保持完全不变，修复次数0。

未执行：排练、真人评审、观众测试、控制A/B、视频生成、平台发布、季集扩写、Skill或metadata编辑、commit/push。只对本次fixture落盘；没有为通过提示而补字。结果属于一次新模型执行样本，不能泛化为Skill整体质量认证。

交付文件：prewriting_outline.md；story_contract.json；preflight.json；EP01.raw.md；initial_diagnostic.json；editorial_ledger.json；review.json；manual_review.md；run_order.md。
