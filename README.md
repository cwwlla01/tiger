# Tiger 短剧全流程 Skills 合集（V2 统一对齐版）

面向 AI / 3D 短剧生产的全链路 Skill 套件，打通 **原创前置立项** 与 **小说改编提取** 双入口，覆盖从一句话梗概到分镜、提示词与独立 QA 验收的完整闭环。

## 双入口生产流水线

- **入口 A｜原创剧本（推荐先锁预算与资产，再开写）**
  ```text
  $tiger-drama-architect (00 立项/规则/人物妆造锁/分集因果/ep000胶囊)
    → $tiger-drama-assets (02 模式A：前置建库锁全季常驻资产白名单)
    → $tiger-drama-writer (01 按集写正文 + 滚动状态胶囊 + 每5~10集 audit_batch 体检定稿)
    → $tiger-drama-assets (02 模式B：按集同步伤势/污损/小道具增量)
    → $tiger-drama-director (03A 专业导演分镜) 或 $ai-storyboard (03B AI快产分镜)
    → $tiger-video-prompt (04 静帧 + 05 视频提示词)
    → $tiger-drama-qa (06 跨文件独立验收)
  ```
- **入口 B｜小说改编 / 已有成品剧本**
  ```text
  $tiger-drama-writer (01 改编定稿) → $tiger-drama-assets (02 提取建库) → 03(A/B) → 04/05 → 06
  ```

## 目录与 Skill 清单

| 目录 | 定位 | 核心产物 / 作用 |
| --- | --- | --- |
| `tiger-drama-architect` | **00 原创前置策划** *(新增)* | 故事圣经、`world/rules.md`、`world/characters.md`（含防剧透标签与常驻妆造预算锁）、分集因果大纲、`state_capsule_ep000.json` |
| `tiger-drama-writer` | **01 剧本创作与审查（V4.25）** | 完整可演剧本、单集切片器 `build_ep_context.py`、硬校验 `lint_script.py`、5～10 集批次体检 `audit_batch.py`（通过后默认直接覆盖） |
| `tiger-drama-assets` | **02 资产与造型连续性** | 双模式（前置建库 + 剧本增量），维护 `CHAR/PROP/SCENE/MONSTER → Stage → Look` 全局库与 `02-资产解析.md` |
| `tiger-drama-director` | **03A 专业导演分镜** | 复杂剧情、多人物调度与完整视听设计（`03-专业导演分镜.md`） |
| `ai-storyboard` | **03B AI 快产分镜** | 面向 Seedance / 大批量快节奏单集拆镜（`03-AI导演分镜.md`，兼容 `SH/T` 与 `02 ID`） |
| `tiger-video-prompt` | **04/05 提示词编译** | `04-画面帧生成提示词.md`、`05-视频生成提示词.md`（同时兼容 03A 与 03B） |
| `tiger-drama-qa` | **06 独立质量验收** | `06-全流程验收报告.md`、`06-问题清单.json` 与跨文件一致核验 |
| `tiger-drama-orchestrator` | **制作总控调度** | 状态扫描、断点续跑、版本 SHA 复用与返工调度（`00-生产总控状态.json`） |
| `tiger-shared-references` | **公共接口契约** *(非 Skill)* | `pipeline-contracts.md`（双入口流程、单集同级文件命名与跨阶段 ID 规范） |

## 安装

将根目录下的全部 Skill 文件夹（`tiger-drama-*`、`ai-storyboard` 以及可选公共参考 `tiger-shared-references`）复制到你的 Skills 目录：
- Codex：`~/.codex/skills/` 或 `C:\Users\<用户名>\.codex\skills\`
- 已存在同名旧目录时，请先备份或直接用本版覆盖（本版已统一同步 `tiger-drama-writer` V4.25，无需再单独安装额外压缩包）。

## 常用调用

```text
$tiger-drama-architect     # 原创从零立项与人物/大纲/初始胶囊
$tiger-drama-writer        # 按集写剧本、续写或运行 5~10 集阶段体检
$tiger-drama-assets        # 前置锁全局白名单或单集资产增量解析
$tiger-drama-director      # 高复杂度单集专业导演分镜
$ai-storyboard             # 大批量 AI 视频精简分镜
$tiger-video-prompt        # 编译 04 静帧与 05 视频提示词
$tiger-drama-qa            # 独立跨文件 06 验收
$tiger-drama-orchestrator  # 多集断点与全流程总控
```
