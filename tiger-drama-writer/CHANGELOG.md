## V17 候选版——对抗决策闭环
- 区分不可行、偏好和即时承诺。
- 保留对手的认知、备选项和合理拒绝。
- 采用 PASS/UNVERIFIED/BLOCKED 三态证据门禁；不得编造正典。
- 不增加交付物，也不修改剧本。

# 更新记录

## V3.56
- 经新一轮五集创作失败后，新增按场景预算创作的流程。
- 要求每场戏明确目标、反制、策略变化、对白作用、后果和连续性状态差分。
- 要求立即运行场景与单集门禁，首次失败就停止。
- 明确禁止凑篇幅，并将不可变原稿与修订稿分开保存。
- 如实报告回归结果：新五集批次未通过验收；本次改动是流程修正，不代表生成质量已提高。

## V3.57
- 进行了真实的逐集创作检查点，冻结原始剧本、分集证据和顺序清单。
- 明确禁止事后重建所谓的顺序运行过程。
- 自审必须明确标记为自审，不得冒充独立验证。

## V3.58
- 测试了从冻结且自审过的 EP01 直接续写新 EP02；保留原 EP01，并保存 EP02 初稿及其独立证据记录。
- 新增明确的状态承接及证据可信度区分；禁止在续集中把未核实的目击说法、照片或医院记录变成既定事实。
- 两条顺序剧集记录通过流程验证；两者仅达到静态就绪并完成自审，未经独立批准。

## V3.59
- 将 EP01–EP02 的真实顺序试写扩展至 EP03，保存不可变初稿和绑定源哈希的自审记录。
- 新增有限揭示和文件保管说明，区分申请回执、照片、证词与独立确认。
- 明确保留情绪质量和实测时长尚未验证的限制。

## V3.60
- 在 V3.59 完成 EP01–EP03 后，顺序完成 EP04 和 EP05 初稿；五集整体检查。
- 新增五集批次结束证明和连续性台账要求，将机器筛查与艺术/时长验收分开。

## V3.61
- 新增绑定证据的连续剧集主导机制多样性审查；若连续三集声明相同机制，或引文不在其所指剧集中，则拒绝通过。
- 将 EP04 结尾改写为受限条件下的安全选择行动，同时保留跟踪者身份不确定性及后续设备通知。
- 静态台账验证不能替代人工类型、情绪或时长审查。

- V3.62: Voice-through-choice and emotion payoff drafting protocol with bounded example; no blind-reader or measured timing claim.

- V3.63: Fixed blind-voice card-ID ordering information leak; removed public episode clues; excluded identical cross-speaker lines and role-name mentions; added independent-key protocol and regression tests. Added explicit dialogue/action runtime feasibility proxy without falsely claiming measured screen time. Historical five-episode script is outside 90–150s proxy range for all episodes, so timed readiness remains unproven.

## V3.64 (2026-10-29)
- Conducted actual EP04 duration-compression experiment with immutable original compression and separate targeted revision.
- Captured static failure of first compression and static success of revision; proxy remains uncertain (111–230s) and is NOT timed acceptance.
- Added stage-led rewrite sequence and strict separation of possible runtime feasibility vs measured 90–150s acceptance.

## V3.65
- Add provenance-bound, per-beat shot timing plan verifier. Distinguish planned seconds from measured runtime; require explicit action/dialogue overlap, enforce sane speech speed, duration and hash integrity.
- Regression fixture for EP04 revision1 and negative tests for mutated scripts, missing overlap, impossible delivery and excessive budget. This is planning validation, not film/rehearsal certification.

## V3.66
- 修复时长计划对白未逐节拍绑定原稿，可能虚构或重复计算对白时间的问题；新增完整对白行映射、动作原文锚点及节拍语速检查。
- EP04 129秒旧计划升级为对白/动作溯源计划，记录机械可过与真人实测缺席的边界。

## V3.67
- Add `scripts/audit_rehearsal.py` and eight positive/negative unit tests for user-supplied rehearsal timing records: hash-bound provenance, two complete takes, complete scene seconds, transitions, actions, dialogue, safety checks, no omitted content, and 90–150-second range.
- Keep rehearsal template explicitly `not_performed`, never generate purported real stopwatch data. A mechanically passing synthetic unit-test fixture is not a real observed rehearsal.
- Separate editable production timing plans, reported rehearsal metadata, independently verified evidence, and artistic acceptance.

V3.68: reject duplicate rehearsal evidence references; parse timezone-aware ISO timestamps; publish field-capture protocol and unperformed template; add four regression tests.

## V3.69
- Added `scripts/audit_emotion_arc.py` with ordered, unique, per-scene and SHA-256-bound evidence validation for pressure → costly choice → visible cost → relationship shift. Artistic verdict remains human-only.
- Added seven adversarial unit tests for mismatched hashes, fabricated/duplicated citations, scene mismatches, reversed chronology, and absent consequence.
- Tested against unchanged real EP04 script; four quotes located once in correct scene order; no independent reader/rehearsal claim.

## V3.70
- Added `audit_voice_panel.py` to validate genuinely collected external blind dialogue responses against a source-bound anonymous pack and separated answer key; reports confusion and majority-class baseline without claiming to verify real reader identity.
- Added nine adversarial tests; conducted real five-episode card extraction and a zero-reader rejection (no fabricated respondents).
- Human emotional-quality and read-through timing acceptance remain unperformed.

## V3.71
- Added `scripts/audit_emotion_panel.py`, a provenance-bound panel auditor for 4 emotional quality dimensions, >=3 independent reader records, evidence uniqueness and qualitative feedback.
- Added 9 adversarial/positive tests, and `references/emotion_panel_UNCOLLECTED.json` for EP04. The blank panel correctly fails validation; no fake human scores generated.

### V3.72
- Added `feedback_triage.py` to convert **real, mechanically validated** voice/emotion panels into provenance-preserving editorial revision candidates.
- Empty/invalid panels generate no synthetic scores or revision targets. Human scene-level review and a fresh post-rewrite panel remain mandatory.

## V3.73
- 新题材独立首稿《请勿签收幸福》EP01 静态检查通过，时长代理下界161秒、上界313秒，发现先前跨题材超时问题仍然存在；绝不宣称成片时长达标。
- 增加 `scripts/firstpass_dual_gate.py`，联合报告静态与时长代理风险；即使两项正常，也不伪造编辑或排练授权。
- 增加联合闸门4项测试和不可变首稿审计数据。

## V3.74
- 修复首稿双闸门把 `UPPER_EXCEEDS_TARGET` 直接认作强制重写的误判；新增 `requires_beat_plan_or_rehearsal` 与 `time_decision`，仍保持未获编辑授权状态。
- 实际改写都市轻喜剧《请勿签收幸福》EP01：原稿624对白汉字、161–313秒；第一次修订363字、109–226秒；原稿与修订稿均静态通过。真实排练计时依然缺失。
- 新增不确定上限的测试用例，禁止因为保守上限超标而盲目删薄场景。

### V3.75
- 修复逐节拍动作引文只验证“正文出现”的漏洞：现在须为舞台动作行，重复或倒序的动作引文会被阻断。
- 拦截所有动作时间一律与对白重叠的乐观预算；各场报告独立动作秒数。
- 《请勿签收幸福》EP01定稿未更改，新增可溯源的132秒拍摄计划（42/42/48秒），其中独立动作28秒；仅为计划值，非排练实测。
- 新增4个针对性回归用例（含全重叠风险）；自动回归81项通过。

## V3.76
- 新增 `audit_continuity_delta.py`，检查相邻两集的状态差分、唯一原文锚点、脚本哈希、未解释状态变更及重复变更；编辑负责语义正确性和字段覆盖。
- 新增六项针对性单元测试，杜绝把账本一致性误报为60集长篇质量已验证。

## V3.77
- 修复跨集状态账本禁止合法新增字段的问题：增加 `introduced` 明确登记机制，禁止漏登及重复登记。
- 阻断空状态账本和无效状态值；旧追踪字段不得静默丢弃。
- 新增6项针对性单元测试；使用《病历上的空白》EP01→EP02 原始剧本做正反对照。
- 仅保证账本原文溯源与字段一致性，不宣称60集长篇质量已经获得验证。

### V3.78
- Added `scripts/audit_continuity_chain.py` and 5 focused tests: checks that every adjacent ledger passes its own audit, the middle episode is byte-identical, and the previous-state snapshot of the next ledger exactly equals the current-state snapshot of the preceding ledger.
- Ran the chain on genuine EP01–EP03 script files with explicitly scoped editorial state ledger; negative tampering test rejects mismatched state handoff.
- Explicitly states untracked facts and artistic coherence are not certified.

## V3.79
- 新增 `continuity_coverage.py`：从具体剧本动作与对白发现连续性候选，保存剧本哈希、场次、行号和原文。
- 新增候选处理复核：追踪、已有追踪、带理由驳回或暂缓；任何漏处理、重复、过期哈希、暂缓都不放行。
- 新增10项针对性测试；全套108项单元测试通过。真实《病历上的空白》EP02识别33条候选，空白记录拒绝放行。
- 本工具只是非穷尽关键词线索，不能自动发现所有连续性事实或代替真人编辑。

### V3.80
- 对连续性候选扫描做保守降噪：排除孤立的「知道/不知道」表达，但保留具体姓名、监控、物件与伤势线索；加入高风险/待复核分层和按场次导航。
- 审计仍按每条候选 ID 强制逐项处理，防止批量导航掩盖漏登记。
- 在《病历上的空白》EP02 上重新验证，并增加4项针对性回归测试。

### V3.81
- 修复连续性扫描中“每条舞台动作自动高风险”的分级漏洞。普通持有或看向物品属于普通复核，明确伤势及道具移交仍优先。
- 《病历上的空白》EP02 真实复测：候选32条不变，高优先级18→14，普通复核14→18；没有省略任何候选的逐条审核要求。
- 新增4项正反测试，总计116项单元测试通过；此结果仅表明分级行为符合预期，未证明艺术质量或长篇完整性。

## V3.82
- 修复候选处理记录 `track` / `already_tracked` 只需任意非空 `state_key` 就可冒充已跟踪的漏洞。
- `continuity_coverage.py --ledger` 通过剧本哈希绑定实际状态差分账本，检查新增键是否登记于 `introduced`、既有键是否存在于 `current_state`。
- 新增6项单元测试，完整122项单元测试通过。机械关联不是独立编辑确认，也不保证全部故事事实被发现。

## V3.83
- 修复状态链重放漏洞：同一 ledger 或同一对剧集被重复作为新转接时拒绝；前后剧集字节完全一致时拒绝。
- 状态链读取异常显式报告失败，避免部分文件缺失时静默宣称有效。
- 新增3项针对性单元测试；真实《病历上的空白》三集通过，历史转接重放被正确阻断。
- 本版不涉及新剧集生成、独立读者反馈或真人计时。

## V3.84
- Hardened the multi-episode ledger chain against same-content replay under different filenames by SHA-256 fingerprints of ledger bytes.
- Rejected a later episode whose body is identical to any earlier episode, even if the paths differ.
- Added two regression tests for replay-by-copy and later-episode content reuse; the existing real three-episode chain remains valid.

- V3.85: Support explicit editor-attested carry-forward anchors for tracked facts not restated in each episode. Preserve original-quote checks for quoted anchors, and real five-episode continuity chain regression. Avoid padding script with recurring state recaps solely for static audit.

## V3.86
- Carry-forward statements must include an independently verifiable original source-script path, SHA-256, and exact unique quote; a bare editor checkbox no longer suffices.
- New negative tests reject missing sources, invalid hashes, fabricated quotes, and unreadable scripts. Historical five-episode source ledgers updated with actual EP02 provenance.
- This is evidence provenance, not proof that no untracked intermediate state change occurred; no new episodes or live performance tests.

## V3.87
- 修复 carry_forward 历史引用虽然哈希正确但来源处于当前链外的漏洞。
- 修复状态键在中间剧集已发生登记变更，却继续引用更早旧证据的漏洞。
- 新增真实五集独立夹具及三项正反回归测试；注明人工审查局限。


## V3.88 (2026-10-29)
- 修复一条原文引文无说明支撑多个独立状态的审查缺口；合法共证情形采用 `shared_evidence_reason` 显式说明，避免误伤真实动作。
- 检测 `previous_anchors` 中未追踪的多余状态键。
- 新增4项专门回归，五集历史状态链仍通过；142项单元测试通过。本版不证明60集实际生成质量或真人拍摄时长。

### V3.89｜回归样本可移植，禁止缺失样本静默跳过

- 修复历史测试读取 `/mnt/data/v82`、`v84`、`v86` 和安装包父目录 `trials/` 的硬编码依赖。固定回归样本随 Skill 打包到 `tests/fixtures/`。
- 去掉关键回归的 `exists()` 条件跳过；缺样本必须失败。新增 `test_portable_fixtures.py` 防止路径回退。
- 全部145项单元测试通过，并在独立目录重新运行，确认回归自包含。本版本不声称新增长篇剧本或真人计时数据。

## V3.90 (2026-10-29)
- Added a genuinely new three-episode, unedited community-family-comedy fixture with separate files and preserved first-pass SHA-256s.
- Added four portable regression tests ensuring all three source scripts pass static screening without confusing structural success with timed-runtime or editorial approval.
- Added actionable pre-draft stage-budget and conflict-diversity instructions, recording upper-bound runtime uncertainty (127–256, 132–265, 135–270 seconds) without claiming rehearsal acceptance.

## V3.91
- Ran a new raw EP04 in the existing community-family comedy project; static-ready but 158–308s runtime proxy, a genuine stop-gate failure.
- Retained unchanged raw first pass and saved targeted revision separately. Revision remains static-ready, 32 dialogue turns and three scenes, proxy 138–275s: lower bound improved, upper bound still unverified.
- Embedded real raw/revision fixtures and three portable regression tests to keep the first-pass failure and partial repair auditable.
- No independently approved review, measured rehearsal, EP05, or full five-episode authorization claimed.

## V3.92
- 新增对白均长与时长敏感性诊断脚本 `dialogue_runtime_tradeoff.py`；把试跑的真实首稿/修订稿内置为可移植回归样本。
- 生成规则明确避免为清除短对白警报而机械扩写；记录最低必要增量与时长代价，定点修订后重新检查，静态检查或代理模型均不等于艺术质量和实测时长。
