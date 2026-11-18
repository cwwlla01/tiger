# 多模态素材引用
每个槽位写 slot、modality、asset_or_frame_id、actual_file_or_provider_ref、purpose、uploaded、approved、model_capability、status。用途如身份/服装/场景/道具/首帧构图/尾帧构图/动作参考/运镜参考/音色。
`@图片1` 是占位标签，只有真实文件已上传且型号引用语法已核实才可标READY；否则写 `@图片1 [待绑定：F-T012-START]` 和PLACEHOLDER，不把内部资产ID冒充已上传图。不得虚构@视频、@音频或上限。
