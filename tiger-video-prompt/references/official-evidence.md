# 官方来源与证据等级
字节跳动 Seed 官方发布《Seedance 2.0 正式发布》，2026-02-12：https://seed.bytedance.com/zh/blog/official-launch-of-seedance-2-0
官方发布说明：Seedance 2.0 系列支持文字、图片、视频、音频混合参考；示例包含 `@图片 1` 并分别指明分镜、人物、场景、道具参考用途；提及9图/3视频/3音频、15秒多镜头、编辑、延长及音频能力。**系列级功能不自动代表每个具体入口都具有全部能力。**

型号专项补充（2026-11-17）：官方 BytePlus 模型文档逐型号列出 Seedance 2.0 Fast 的时长范围为4–15秒；视频生成 API 说明 `duration` 为整数秒，`-1` 表示自动时长。来源：[Seedance 2.0 model guide](https://docs.byteplus.com/de/docs/modelark/seedance-2-0?redirect=1)、[video generation tutorial](https://docs.byteplus.com/de/docs/modelark/video-generation-tutorial)。本项目要求精确时长，因此使用4–15秒整数，不使用自动值。即梦官方生成器说明按当前模型选项设置时长。该型号范围可复用，不必每次重新搜索；只在型号、官方规格或实际 UI 行为改变时更新。
证据等级：OFFICIAL_FAMILY（系列官方）/ MODEL_VERIFIED（具体型号入口官方或截图）/ WORKFLOW_HEURISTIC（本技能制作建议）/ UNKNOWN（无证据）。
逐型号核验：显示名、入口、核验日期、来源、图/视频/音频输入、引用语法、时长、画幅、首尾帧、多镜头、编辑/延长。未知一律 UNKNOWN，不借用其他型号参数。
