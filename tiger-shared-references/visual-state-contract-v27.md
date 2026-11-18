# V2.7 统一镜头视觉状态契约

## 核心原则
- `03` 为权威导演视觉状态，`04` 静帧与 `05` 视频必须继承，不得静默修改。
- 三层继承：系列视觉基准 → 场景视觉基准 → Take 差异覆盖；记录引用 ID，不在每个镜头复制整份风格描述。
- 每个 Take 使用稳定 `take_id`；03/04/05 对应同一镜头，任何新增或拆分须有来源与导演批准。
- 核心字段：`series_look_ref`、`scene_look_ref`、`character_asset_ref`、`material_ref`、`world_light_refs`、`camera`、`composition`、`palette`、`weather`、`motion`、`face_light_claims`。
- `camera` 记录世界位置、朝向及必要镜头轨迹；`world_light_refs` 指向场景固定光源 ID；`face_light_claims` 记录面部直接受光状态的导演预期。
- 03 中未填写的可选字段不代表 04/05 可自行重导演；如需新增决定，应回传导演审核。
- 视觉契约只验证结构与交接。世界光源投影、光区穿越、面部受光需分别调用既有专项检查器；实际画面仍需独立视觉验收。

## 交接示例
```json
{"schema_version":"2.7","stages":{"03":{"takes":[{"take_id":"T-001","series_look_ref":"SERIES-A","scene_look_ref":"SCENE-A","character_asset_ref":"CHAR-A","material_ref":"MAT-A","world_light_refs":["L1"],"camera":{"position":[0,0,2],"forward":[0,1,0]},"composition":{"type":"thirds"},"palette":"cool-white","weather":"indoor","motion":{"start_s":0,"end_s":3},"face_light_claims":[{"light_id":"L1","status":"front_lit"}]}]},"04":{"takes":[]},"05":{"takes":[]}}}
```
示例中 04/05 为空仅为结构说明，真实交接会被 QA 判定为缺失。
