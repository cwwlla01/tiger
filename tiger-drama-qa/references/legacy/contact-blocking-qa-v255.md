# V2.55 走位闭环独立审查
- 检查候选空间布局是否标记 PROPOSED，是否有经核验的场景母版/预演证据。
- 若证据缺失，S07=BLOCKING_REQUIRES_LAYOUT，不能 ACCEPTED_FOR_PRODUCTION。
- 其余不依赖 S07 接触几何的 Take 可独立通过结构门禁；S09=EDIT_AUDIO_ONLY。
- 真实接触和声画同步必须在视频/音频成品复核，文本测试不代表视觉验收。
