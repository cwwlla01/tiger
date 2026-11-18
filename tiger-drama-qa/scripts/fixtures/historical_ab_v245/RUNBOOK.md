# V2.45 历史版本 A/B 执行包（尚未运行）

1. 冻结 `frozen_scene.json`，校验 manifest 中 SHA256。
2. 分别在互相隔离的上下文加载原始 V2.38 / V2.39 导演 ZIP，严禁注入 V2.45 规则。
3. 每次只输入冻结场次，生成原始 `03-专业导演分镜.md`，不互看另一组结果。
4. 记录 `run.json`（run_id, arm, source_zip_sha256, scene_sha256, output_sha256, timestamp, model, settings, independence_attested）。
5. 运行 `audit_historical_execution_v245.py`，只有独立输出证据齐全才进入结构评价；艺术质量需额外盲审。

本包仅含执行计划与冻结输入，不含声称由旧版模型生成的产物。
