# V2.22 跨场景/跨集导演风格连续性合同

## 目的与边界
风格不是统一滤镜或固定景别。先从剧本、世界观、已批准视觉圣经和前集冻结的03提取**有来源的**作品级视觉语法；缺少权威来源标记 `STYLE_AUTHORITY_UNRESOLVED`，不可擅自定为已批准风格。剧情需要的风格偏离允许存在，但必须有源事件、人物主观视角或导演明确意图支持，并保留 `style_exception_reason`。不得以风格一致性覆盖角色阶段、场景实际光源、时间、天气、资产版本、剧情真实信息。

## 作品级合同 `style_bible`
- `bible_id`、`bible_version`、`authority_anchor`、`project_id`；版本冻结后变更需审批。
- `visual_grammar`：机位倾向、景别使用原则、镜头运动动机、色彩对比、光影原则、空间深度、镜头停顿逻辑，均以**叙事功能**表达，禁止无条件固定数值。
- `dramatic_rhythm`：紧张升级/释放原则、悬念揭示边界、角色反应优先级。
- `motif_registry`：重复视觉母题的 `motif_id`、首次源锚点、允许出现条件、禁止出现条件；母题不可凭空制造故事线索。

## 场景合同 `scene_style`（03）
- `scene_id`、`source_anchor`、`bible_id`、`bible_version`、`style_mode` (`BASELINE`/`JUSTIFIED_DEVIATION`)、`style_intent`、`attention_rule`、`rhythm_rule`、`motif_ids`、`style_exception_reason`。
- 允许同一作品中冷暖/快慢/景别形成对比；`JUSTIFIED_DEVIATION` 必须明确理由，不能被 QA 自动改回统一风格。
- `motif_ids` 只引用作品圣经中已批准的母题，且场景具备相应出现条件；跨集重复必须有新戏剧功能，不得机械重复。

## 04/05 编译与 06 验收
- 04只继承可在单帧观察的色彩、光位、构图、空间与母题状态，不把节奏过程伪装成静态帧。
- 05继承场景的节奏规则、运镜动机、母题出现时机；若模型限制导致无法执行，标记 `EXECUTION_BLOCKED` 并退回，不得静默更改03。
- 06逐场对比冻结03的 `scene_style` 与04/05声明，核对跨集 `bible_id/version`；结构脚本仅识别字段、顺序和引用漂移，艺术风格与叙事正当性需人工结合来源判断。
