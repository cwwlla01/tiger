# Tiger Skills 优化合集

本包包含全部 Tiger Skill、`ai-storyboard` 以及公共 references。

## 包含内容

- `tiger-drama-assets`：资产、Stage、Look 与跨集连续性管理
- `tiger-drama-writer`：剧本创作、续写、修订与文本审查
- `tiger-drama-director`：导演分镜设计
- `tiger-drama-orchestrator`：单集/批次流程调度
- `tiger-drama-qa`：独立质量审核
- `tiger-video-prompt`：静帧与视频提示词编译
- `ai-storyboard`：面向 AI 视频生成的精简高质量分镜
- `tiger-shared-references`：多个 Tiger Skill 共用的参考文件

## 安装

将解压后的所有文件夹复制到：

`C:\Users\zero\.codex\skills\`

如果目标目录已经存在，请先备份旧目录，再覆盖同名文件。

建议同时安装 `tiger-drama-writer-optimized.zip`，这样剧本、资产、分镜、提示词和 QA 的版本保持一致。

## 常用调用

```text
$tiger-drama-orchestrator
$tiger-drama-assets
$tiger-drama-director
$tiger-video-prompt
$tiger-drama-qa
$ai-storyboard
```

单项任务优先显式调用对应 Skill；不要为只做资产解析的任务自动启动完整制作链路。
