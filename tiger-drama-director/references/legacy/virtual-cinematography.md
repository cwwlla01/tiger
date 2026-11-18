# 虚拟摄影机系统 V2

## 三级摄影控制
1. 系列视觉基准：画幅、摄影风格、稳定性、光影与景深原则；不虚构真实机身的模型能力。
2. 场景基准：场景几何、门窗、轴线、视线、灯光、禁穿越区域、镜头衔接。
3. 逐镜头：景别、机位角度/高度、主体构图、主运动ID、运动路径、速度、起止状态；光学/时间/视角修饰按需。

## 逐镜头字段契约（语义字段，不要求所有输出用YAML）
- `camera_primary_id`: 单个主要摄影运动ID，静止用 CAM-01；不可用 POV/慢动作冒充主运动。
- `perspective_ids / optical_ids / temporal_ids / transition_ids`: 可空的附加技法ID列表。
- `shot_size / camera_height / angle / screen_axis / subject_screen_position`: 必填。
- `start_composition / end_composition / start_state / end_state`: 必填。
- `trajectory / direction / orientation / speed_phases / duration`: 运动镜头必填；静止镜头写 `NONE`。
- `lens_visual / focus_behavior / depth_of_field`: 条件选填；焦距用全画幅等效视觉参考，不承诺真实毫米级控制。
- `dramatic_intent / audience_information / continuity_constraints / ai_risk / fallback / implementation_route`: 必填；`implementation_route` 选生成、3D、后期、混合。
- `camera_design_version`: 可选；03权威母版中变更时同步版本与受影响 Take。

## 摄影轨迹语法
写清起点（相对角色/场景）、路径（方向、弧度、高度）、速度阶段（起步/运动/停机）、主体画面锚点、终点、不可穿越的实体。示例：0–1s 低机位静止；1–4s 从角色左前方沿顺时针弧线环绕并抬升；4–5s 减速停于右前方高机位，主体始终居中。不可用“高级电影感”替代轨迹。

## 约束
真实摄影机品牌/型号仅作为风格参考；镜头焦距、快门、景深等数值未经实际模型验证时只能表达视觉意图。先保证空间/因果/角色可读性，再考虑炫技。不得改变原剧本和既有资产版本。
