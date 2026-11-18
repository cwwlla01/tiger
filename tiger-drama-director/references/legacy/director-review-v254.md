# V2.54 真实场次导演复审

针对 03 的逐镜头复审，先查源事件、空间几何、动作因果、镜头/Take 边界、声音和观众信息边界。不能把“固定镜头内切近景”视为单 Take；可拆生成 Take 而保持编辑镜头与源事件关系。接触动作缺少几何证据时标记 `BLOCKING_REQUIRES_LAYOUT`，不得编造人物位置或瞬移。纯黑、字幕、静止卡及音效可选择 `EDIT_AUDIO_ONLY` 等后期任务，不强制调用 AI 视频。金光式蓄势不得成为机械延长镜头的理由。示例及局限参见 QA 的 `fixtures/v254-scene-review/DIRECTOR_REVIEW.md`。
