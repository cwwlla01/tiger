# 即梦视频模型动态兼容目录

本目录是**发现/核验协议**，不是声称覆盖实时官方型号的静态列表。产品命名、地域、账号与 UI 可能变化。

## 已知用户选择
- `Seedance 2 Fast`：本项目当前单一主用型号（用户确认；官方资料名为 `Seedance 2.0 Fast`）。官方模型文档给出的生成时长是**4–15秒，整数秒**；即梦生成器按所选型号设置时长。可选值直接按 `4, 5, 6, ... 15` 秒规划，不必每集或每镜重新搜索。
  - 官方证据：[BytePlus Seedance 2.0 model guide](https://docs.byteplus.com/de/docs/modelark/seedance-2-0?redirect=1)（逐型号列出 Fast 的 `[4, 15]` 秒范围）；[BytePlus video generation tutorial](https://docs.byteplus.com/de/docs/modelark/video-generation-tutorial)（说明 Seedance 2.0 系列支持 `[4, 15]` 或自动时长；时长参数为整数秒）；[即梦 AI 视频生成器](https://jimeng.jianying.com/tools/ai-video-generator)（按当前型号选项设置）。
  - 规划时每个生成 T 直接选一个具体整数秒数，范围4–15秒；不得把15秒当默认值。超过15秒的连续动作拆成多个有连续性边界的T。只有用户报告型号改版、官方规格更新或生成器拒绝已选值时，才重新核对并更新本卡。
  - 每个T的生成长度按动作/台词完成需要选择；剪辑目标可以短于生成片段，多余部分在剪辑中裁掉。不得把SH剪辑目标直接复制为T生成时长，除非确实合适且在4–15秒内。

## 其他即梦视频型号
- 用户可在当前即梦界面选择的**任何视频型号**均纳入编译范围，按界面精确显示名建立记录，不凭猜测枚举型号或把图像模型误认为视频模型。
- 用户要求“全部型号”时：如有官方当前模型列表/界面，逐项提取并记录；如无访问能力，交付**动态通配兼容**，并说明未完成实时型号穷举。

## 型号核验卡
```yaml
provider: 即梦
model_display_name: Seedance 2 Fast
official_family_name: Seedance 2.0 Fast
model_id_if_verified: null
capability_source: https://docs.byteplus.com/de/docs/modelark/seedance-2-0?redirect=1
capability_verified_at: 2026-11-17
supported_inputs: 待核实
duration_options: 4-15s inclusive, integer seconds
aspect_ratios: 待核实
audio_options: 待核实
reference_modes: 待核实
unknowns: [准确界面显示名可能随账号/地区变化, 即梦入口可能因账号/地区展示差异, 其他输入模式]
status: DURATION_VERIFIED
```

只把有可复核来源的字段升级；本型号4–15秒整数时长已核实，其他输入能力仍保持未知。不得因其它字段未知而重复检索已确认的时长，也不得借用其他型号的参数。

## 提示词生成
1. 固定导演母版的身份、动作顺序、机位、起止状态。
2. 先生成模型无关的中文语义提示词。
3. 读取目标型号能力卡；只添加被证实支持的参考图、声音、时长等模型特有参数。
4. 未证实能力只写 `待按当前界面核实`，不把图片或音频要求伪装成模型可执行参数。
5. 写回 `### 视频生成提示词｜即梦 <model_display_name>（主用）`；同一 Take 额外型号使用 `（备选）`。
