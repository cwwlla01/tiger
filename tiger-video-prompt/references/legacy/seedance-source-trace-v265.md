# V2.65 | 05 复制块与真实来源的交叉证据门禁（当前优先）

## 何时运行
用户要纯描述→直接描述，不做05；用户要剧本→01；要分镜→03；明确要 Seedance 2 Fast 完整视频提示词→05。优先沿用 V2.64 对精确渠道、动态时长、单镜头和理由充分的合并判定，**不强制15秒/多镜头/图参模式**。新编译的05在内部使用 `scripts/audit_seedance_fast_v265.py plan.json`，再由独立06跑 `scripts/audit_seedance_fast_v265_independent.py plan.json`。历史V2.59/V2.60仅用于其原六题回归与旧格式，不是通用新稿门禁。

## V2.64 的已证实假阳性
1. `visible_payoffs` 声称蓝瞳蓝发，真实 `prompt` 只写黑发/正常眼睛，V2.64仍通过。
2. `source_approved_voiceover=true` 无脚本来源，却能让旁白通过。
3. `narrative_style_source=approved_project` 只贴标签、不提供项目原文，能让强布袋戏风格通过。

V2.65 用**原文+复制块的精确子串证据**阻断上述无证声明。新脚本基于V2.64的动态时间和合并校验，额外读取真实01候选或批准文件的字节 SHA256；来源原文或文件发生漂移必须退回，不能凭哈希文本或文件名宣称已读取。

## 内部 manifest 字段（绝不能塞进用户的复制块）

- `source_document`（可选）：`{path, sha256, role, authority}`，实际可读取时从**真实字节**计算hash。直接聊天一句话没有可读取01文件时不虚构路径；产出 `CANDIDATE` 并在内部标源事实需要人工对照。
- `director_document`（存在03时使用）：与 `source_document` 一样写入真实03文件路径和SHA；`director_shots[]` 每个SH写 `shot_id,director_quote,prompt_quote`。实际03原句与复制块原句都必须存在，镜头映射不能漏项；未提供03时只允许候选而不伪称导演批准。来源与03的语义差异仍须导演和06人工审读。
- 每个 `takes[].visible_payoffs[]`：在已有 `shot_id,at_seconds,visible_result` 外写 `prompt_quote`，必须是**实际完整复制提示词里的原句**，而非审核员想象的改写。若存在真实 `source_document`，另写 `source_quote`，必须能在来源文件里原样找到。多SH的关键句必须出现在该 SH 文字段内，不得用前镜的亮点冒充后镜高潮。
- `critical_events[]`：逐个不可丢事件写 `{id,take_id,source_quote,prompt_quote}`，例如**眼瞳转蓝与头发转蓝是两条**。若源文件可读，源码和05必须均含对应精确引文；这只能验证引文存在，不判断语义等价，也无法自动发现你漏列的第三条要求。
- 源剧本要求旁白时，`takes[].voiceover_evidence` 写 `{origin:'script',source_quote,prompt_quote}`。源文必须真的有 `旁白：`/`诗号：`，复制块也必须确实含该句。没有源文只有用户本轮请求时用 `origin:'user_request'` 并留人工核验；**不得只靠 `source_approved_voiceover=true`**。
- 精确文字叠加 `onscreen_text_evidence` 须给源文件原句与复制块原句；否则把精确文字交后期，并按声画范围标注，不能凭模板伪造。
- 风格非 `NATURAL` 时附 `narrative_style_evidence.source_quote`，必须含用户或权威项目的实际风格要求。`approved_project` 必须能在真实来源文档中定位；`user_request` 引文需人工对照本轮消息，不得脚本自称已获批准。

V2.65在调用旧V2.64代码时仅对**已经真实核对证据**的旁白/文字创建兼容检查标志；从不把原输入的 `source_approved_voiceover` 布尔值视为来源证据。

## 审查边界
`TEXT_STRUCTURE_PASS`=真实SHA与给定原句匹配、复制块确含见证句、已声明的剪辑时间逻辑一致；**不等于**所有原作事实都被选入 `critical_events`、视觉自然、生成模型会按秒数切镜、当前即梦UI支持拟定时长、源版本已获用户批准、实片质量已通过。独立审计必须回读整份01/03/05，主动寻找未列入manifest的遗漏、语义颠倒、光影空间违例。发现不得用补填审核表替代真正修改05。

相对文件路径以 JSON 计划文件所在目录为基准，解压到新机器仍可重新核对源文件；不要在交付样例里冻结开发容器的绝对路径。

见 `examples` 真实前向测试：01候选→03候选→05完整复制块，T01单镜头，未虚构图参、诗号与15秒默认时长。
