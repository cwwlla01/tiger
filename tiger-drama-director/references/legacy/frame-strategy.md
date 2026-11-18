# 连续 Take 帧策略与画面内容合同

## 在生成 Take 层级作出决定
- `NONE`：黑场/仅声音/仅后期，或无需静帧控制。说明理由；不要为了后期音频生成空白黑色视频。
- `REFERENCE_ONLY`：人物/地点/怪物身份或造型参考已足够；无需单独构图帧。
- `START`：需要严格确定入镜构图、地理关系、人物位置、接触动作或身份；结尾可自由发展。
- `END`：少用；仅在供应商支持且结尾构图至关重要、开场无需固定时采用。不得假设供应商支持只用尾帧条件控制。
- `START_END`：首尾状态都关键、摄影机几何兼容、动作符合物理规律，且已核实供应商支持或明确标记为有条件。固定的尾帧姿势可能过度限制动作：应提供 `START` 回退方案。
- `SEQUENTIAL_KEYFRAMES`：用于复杂变化、拆分 Take 或剪辑点的内部规划图。未经核实不得暗示模型支持输入多个中间关键帧。

## 每张实际画面的必填描述字段
1. `frame_id`、用途（`START`、`END`、`K1`）、关联的**take ID**、时间戳/状态，以及准确的源文锚点。
2. 将图像内容描述为**一个静止瞬间**：画面中可见的具名主体、身份/服装、姿势、面部表情、视线、手部/接触和道具持有者、怪物位置与威胁可见程度。
3. 空间图：左右/前景/背景、门/架子/横梁位置、人物间距、屏幕方向与轴线。
4. 摄影：景别、摄影机所在侧、高度、角度、焦点人物、前景层次、景深、光源/色彩/反差、艺术风格。
5. 连续性：哪些内容必须与前/后帧及相邻 Take 一致；帧间允许哪些变化；哪些事件尚不得发生。
6. 所需源资产及其真实状态（`AVAILABLE_VERIFIED`、`NEEDED`、`UNCONFIRMED`），以及生成/身份风险。
7. 说明为何需要此帧、为何不需要其他帧，以及可行的回退方案。

## 合并镜头与编辑切点
- 连续 Take 内的每个编辑节拍不要各自分配一组 START/END。帧 ID 属于外层 Take；中间编辑节拍用时间/动作备注描述。
- 若合并的5秒 Take 包含真实摄影机切点、场景跳转、不兼容的摄影机方向，或多段各自复杂的互动，应测试供应商的多镜头行为，或拆分成多个 Take，同时保留**编辑**顺序。
- 静态 END 图必须表现紧接下一 Take 开始前的状态，不能提前表现更后面的死亡/揭示。不得预演下一个正典事件。
- 避免过量生成帧图：终点不受约束的动作可能只需一张已审查的 START 帧。不得为了证明合并 Take 合理而硬加帧图。

## 示例——救援 Take T-C10（5秒）
`START F-T-C10-START`: storeroom side medium-low shot, doorframe left, Wei at left hand still on frame, Lin on floor right under cracked overhead beam, no sleeve grip yet, cool industrial top light, beam unfallen. Preserve verified character looks.
`END F-T-C10-END` (conditional): identical camera side/room geometry/light; Lin pulled toward room interior, Wei leaning into danger and still gripping Lin's sleeve, beam **not yet fallen**. Maintain plausible arm reach and screen direction.
理由：涉及双人接触及横梁空间关系。优先试用 START；只有确实需要且得到支持时才增加 END；回退方案为抓握动作插入镜头 + 救援结果镜头，并用声音桥衔接。

## 示例——苏醒 Take T-C19
`START`: Lin dark hair, lowered head, breath rapid, same room and costume.
`END`（有条件）：保持同一面孔/身体/服装及摄影机轴线；深栗色头发、琥珀棕色虹膜，抬眼望向门及两只鳄鱼威胁。形态变化不得引入另一个人物或多出一扇门。如果连续变身失败，就在低头状态切开，另用稳定镜头揭示最终身份。
