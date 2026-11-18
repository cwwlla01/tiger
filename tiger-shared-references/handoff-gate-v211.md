# V2.11 证据化交接门禁

## 目标
把 V2.10 停止规则变为可自动回归的生产状态门禁。此清单是可选的结构化审计输入，不改变03/04/05的正式文本格式。

## 字段
根字段：`director_frozen`(bool), `director_hash`(03原文 SHA256), `takes`(array)。每个 Take：`take_id`, `stage`(03/04/05), `delivery_status`(CANDIDATE/FORMAL), `director_hash`(04/05必须与根一致), `geometry_uncertain`, `fallback_shot`, `simulation_rounds`, `new_authoritative_evidence`, `canonical_conflict`, `unapproved_director_change`, `claims_video_qa_passed`, `claims_asset_verified`, `claims_physics_verified`, `evidence`。

## 不可逾越边界
- 03未冻结，04/05不得标为正式；候选编译可以进行但必须明示。
- 有几何不确定性须给具体低风险替代镜头，最多两轮无新证据的简化模拟。
- `video_review` 是真实视频审查记录标识；`asset_verified` 是真实资产核验记录；`physics=simulation` 不能支持“真实物理验证通过”。
- 任何结构化脚本通过只表示字段声明符合门禁，不代表故事质量、物理精度或视频成片通过。
- 对 P0 返回原责任阶段，QA不得擅自改03权威母版。
