# 专业Skill路由与名称迁移

| 环节 | 目标Skill | 当前已知旧入口 | 职责 |
|---|---|---|---|
| 00 | tiger-drama-orchestrator | 无 | 总控调度 |
| 01 | tiger-drama-writer | drama-writer-pro | 剧本创作及修订 |
| 02 | tiger-drama-assets | drama-asset-registry | 四类资产登记、版本、缺口、复用，贯穿全程 |
| 03 | tiger-drama-director | apocalypse-rule-director | 导演分镜、Take与镜头连续性 |
| 04 + 05 | tiger-video-prompt | video-prompt-compiler | 编译04静帧和05视频提示词，保持03只读 |
| 06 | tiger-drama-qa | drama-pipeline-qa 或 drama-production-qa | 独立审核、退回、复验 |

- 以上目标名是迁移目标，不代表对应Skill已安装。先检查当前可用Skill目录，再按存在的真实入口执行。
- 实际生成角色图片时按需路由 `drama-character-asset-production`；怪物按需 `monster-stage-asset-director`；其他实际图像制作按需 `drama-image-director`。这些不是04文本提示词的必经依赖。
- 不将01/02/03三个不同职责命名成同一个 `tiger-drama-writer`。
- 若专业Skill有明确的源文件只读、版本或资产规范，遵守其更严格约束；总控不得自行放宽。
