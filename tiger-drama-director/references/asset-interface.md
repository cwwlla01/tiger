# 导演与资产制作接口：四类资产及跨集复用

## 权责边界
- 导演**读取**项目资产总库，识别所需资产、视觉/摄影约束、逐镜头状态、首帧/尾帧构图和缺口。导演**不负责**最终确定面部身份、服装设计、批准版本、渲染图像或写入正典总库记录。
- 资产制作/总库负责人**分配正典 ID**，定义并批准 individual/stage/look 及图像版本，制作和审查参考图，处理冲突并持久化总库变更。资产制作必须尊重导演的镜头取景与调度；资产提案可以先行交接，不必暂停整个分镜流程。
- 不得虚构已安装的连接器或持久化存储。无法访问总库时，标记 `REGISTRY_UNAVAILABLE`，使用本地临时 ID（`TMP-...`），并说明无法核实历史复用。不得声称已检查历史记录。

## 四类资产层级
`category (CHAR/PROP/SCENE/MONSTER) → individual_id → stage_id → look_id`, with a separately tracked **transient shot state** and **asset version**.
- Individual（个体）：稳定的实体/身体或真实地点/物件；名称和别名不代表身份。一个身体被不同意识占据时仍是同一个 CHAR 个体；控制者/persona 应单独记录。
- Stage（阶段）：持久且可复用的核心变化（身份控制下的身体形态、怪物进化、场景持续性结构变化、道具功能形态变化）。
- Look（造型）：一个阶段内可复用的服装/配饰/视觉布置或外观组合。没有核心变化的换装通常只创建新 look，不创建新 stage。
- 镜头瞬态状态：姿势、表情、临时污迹、道具位置/持有人、瞬时光线、撞击、动作和非持续性损伤。不要为每帧扩增 stage/look 目录。
- 资产版本：已批准的视觉/参考版本，与 stage 和 look 不同；更新时不得暗中覆盖已批准版本。
- 场景/道具变化：区分长期结构损坏（可能需要新 stage）与临时现场状态；根据源文时间线判断。

## 查找与设计规范
1. 阅读实际剧本、可访问的资产总库/已批准资产清单及用户提供的图片。解析别名和跨集出场。优先复用已批准资产；若只有文字批准，不得声称图像已经存在。
2. 处理多集时，先提取全部剧集的实体出场和有序变化，再最终确定 stage/look 提案；检查后续剧本描述是否约束前面尚未明确的外观。
3. 为每项需求标注**来源依据**：`SCRIPT_EXPLICIT`、`APPROVED_HISTORY`、`DIRECTOR_PROPOSAL` 或 `UNVERIFIED`。区分总库状态 `APPROVED`、`PROPOSED`、`NEEDED`、`UNVERIFIED`、`CONFLICT`、`REGISTRY_UNAVAILABLE`；另行区分图像可用状态 `IMAGE_VERIFIED`、`TEXT_ONLY`、`IMAGE_MISSING`、`UNKNOWN`。
4. 若剧本未描述外观但历史记录已批准，应准确复用。若两者都没有说明，导演可以给出*功能性*约束（只有戏剧上有必要时才规定年龄印象，以及轮廓/可读性、摄影距离、服装连续性），也可以选择给出非约束性的 `DIRECTOR_PROPOSAL`；面部/妆容/服装细节最终由资产制作方确定。不得将自创细节冒充源文事实。
5. 若剧本与已批准历史记录矛盾，先检查时间线、别名、stage 变化和 look 变化。记录 `CONFLICT` 及双方来源；不得暗中改写历史，也不得把矛盾当作创建新身份的自动许可。
6. 正典 ID 和版本由总库负责人分配。导演原样使用已核实 ID；否则使用本地 `TMP-CHAR-01` 等临时 ID，并明确请求对齐。不同个体不得复用同一 ID。

## 示例：一个身体，多个阶段
`CHAR-001 / S01 / L01`: 林渊常态, black hair where source specifies; current warehouse costume if approved, otherwise `LOOK_NEEDED`.
`CHAR-001 / S02 / L01`: 阿禾接管同一身体; source-backed dark-chestnut hair and amber-brown irises, body/face base and existing costume inherited unless screenplay explicitly changes them. `persona=阿禾`, `body=CHAR-001`.
A transition take uses `CHAR-001 S01→S02` and records exact before/after state. It does not create a new individual `CHAR-002` just because dialogue names 阿禾.

## 逐镜头/Take 交接字段
`take_id | category | individual_id | stage_id | look_id | approved_version_or_unknown | provenance | registry_status | image_status | transient_state | required_view_or_detail | use(REFERENCE/START/END/KEY) | affected_frames | gap/owner_action`.
在 `03-专业导演分镜.md` 中提供简洁概览和逐 Take 引用；不要默认新增交付文件。即使帧策略为 `NONE`，调度连续性仍可能需要资产。资产需求优先级标为 `BLOCKING`（无法生成该帧）、`HIGH`、`NORMAL` 或 `OPTIONAL`，并写明具体理由。

## 跨集回归测试
- EP001 未提到面孔，EP002 是同一人物：继承已批准的历史面孔；不要再制作一张母版图。
- EP001 黑发林渊，后续由阿禾接管：属于同一个体，创建阶段变化，继承服装；确有需要时才制作两种图像状态。
- 两集中出现同名怪物：对应到已核实的同一个体；不得暗中重复创建。
- 场景中的门损坏延续到下一集：保留损坏后的 stage，或记录其持久状态。
- 无法访问总库：使用临时 ID 并如实标记不确定性，绝不伪造已批准记录。
- 新剧本与已批准服装冲突：标记并交由负责人处理；不要悄悄重新分配 look。
