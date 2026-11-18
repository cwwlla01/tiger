# Tiger 短剧流水线跨阶段统一契约（Single Source of Truth）

本目录为公共参考目录，不作为 Skill 独立调用。所有 Tiger Skill 与 `ai-storyboard` 均遵守以下统一接口。

## 1. 双入口与主干流程

- **入口 A（原创短剧：先锁预算与资产，再写剧本）**
  `00 Architect（立项/规则/人物/大纲/ep000胶囊）→ 02 Assets（模式 A：前置建库锁白名单）→ 01 Writer（受白名单约束按集写作 + state_capsule + 每5~10集 audit_batch）→ 02 Assets（模式 B：增量同步）→ 03（Director 或 Ai-Storyboard）→ 04/05 Video Prompt → 06 QA`
- **入口 B（小说改编 / 已有成品剧本）**
  `01 Writer（改编与定稿）→ 02 Assets（模式 B：全量抽取建库）→ 03 → 04/05 → 06`

## 2. 权威目录与命名规范

- **项目级全局设定与资产**（位于各集目录之外）：
  - `world/rules.md`、`world/characters.md`、`outline/season_outline.md`
  - `全局资产/{人物|道具|场景|怪物}/{名称}-设定.md`、`{名称}-造型.md`
- **单集同级交付**（全部落在 `EPxxx/` 原目录内，严禁另建 `解析/` 或 `审核/` 子文件夹）：
  - `剧本.md`（或 `01-剧本.md`）+ `state_capsule.json`
  - `02-资产解析.md`
  - `03-专业导演分镜.md`（`tiger-drama-director`）**或** `03-AI导演分镜.md`（`ai-storyboard`）
  - `04-画面帧生成提示词.md` + `05-视频生成提示词.md`
  - `06-全流程验收报告.md` + `06-问题清单.json`

## 3. 跨阶段 ID 与状态传递

- **层次编号**：`EP001 → SC001 → SH001 → T-001`。当 `03` 使用 `ai-storyboard` 时，默认 `1 SH = 1 Take`（推荐写法 `### SH01｜T-001｜...`），`04/05/06` 同等视为合法 `03` 权威输入。
- **资产编号**：`CHAR/PROP/SCENE/MONSTER-xxx → Sxx (Stage) → Lxx (Look)`。瞬时血迹、沾灰、手持物与伤势属于镜头/剧本动态状态，通过 `01 state_capsule.json` 传递给 `02`，不滥建新 `Look ID`。
- **独立闭环职责边界**：
  - `01` 管剧情因果、人设声线、集内与 5～10 集批次连续性（`lint_script.py` + `audit_batch.py`）；
  - `02` 管跨集视觉资产与造型版本树；
  - `03A/03B` 管视听镜头执行；
  - `04/05` 管提示词编译；
  - `06` 管跨文件一致性验收（禁止 01/03 擅自修改权威母版）。
