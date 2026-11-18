# 专业Skill路由与职责边界

| 环节 | 目标Skill | 职责 |
|---|---|---|
| 总控 | tiger-drama-orchestrator | 跨阶段状态、依赖、断点与返工调度 |
| 00（原创前置） | tiger-drama-architect | 故事圣经、世界观动线、人物妆造预算锁、分集因果表与 `ep000` 胶囊 |
| 01 | tiger-drama-writer | 剧本创作、续写、修订、状态胶囊与 5～10 集批次体检 |
| 02 | tiger-drama-assets | 四类资产预建白名单（模式 A）及提取/增量（模式 B），维护跨集造型连续性 |
| 03（复杂戏剧） | tiger-drama-director | 专业导演分镜、Take与调度（`03-专业导演分镜.md`） |
| 03（AI快产） | ai-storyboard | 面向 AI 视频生成的精简分镜（`03-AI导演分镜.md`） |
| 04 + 05 | tiger-video-prompt | 编译 `04` 静帧与 `05` 视频提示词，保持 03 只读 |
| 06 | tiger-drama-qa | 独立跨文件验收、退回与复验 |

- 先检查当前可用 Skill 目录再路由；`tiger-shared-references/pipeline-contracts.md` 为公共接口参考，不直接调用。
- 图像/视频实际生图生片工具属于外部可选执行层；不虚构未安装或未触发的外部工具。
- 若专业 Skill 有更严格的只读、版本或资产规范，总控遵守其约束不得放宽。
