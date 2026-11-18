# 模型路由与版本管理

主模型提供方：**即梦**；默认选择 **Seedance 2 Fast**，但**支持用户当前界面中所有可选视频模型**。备用模型：MiniMax H3。

路由优先级：用户明确型号 > 项目默认型号 > Seedance 2 Fast。不同 Take 可选择不同型号；未经要求默认只输出所选主模型提示词。

路由字段：`take_id`, `provider`, `model_display_name`, `model_id_if_verified`, `fallback_model`, `routing_reason`, `asset_status`, `frame_mode`, `model_capability_verified`, `prompt_status`。

型号兼容：对所有即梦视频型号均可生成**模型无关语义层**的导演提示词；只有当前可核验资料证实具体型号支持的输入/输出/控制能力，才编译为“该型号可直接提交”的参数化提示。型号不认识时保留用户给定显示名，标记 `CAPABILITY_UNVERIFIED`，不拒绝，也不虚构支持能力。

- 不基于未经核验的宣传或历史规格断言精确时长、帧数、参考图数量、声音输入、固定画幅或 API 名称。
- 若模型版本发生变化，只重编译提示词与输入参数层，不改导演镜头和已批准资产。
- 如果某型号不支持导演所需控制方式，给出分段/参考图替代方案，保留原始事件覆盖关系，不擅自改写母版。
- H3 备用仅用户要求、风险高或失败证据充分时生成。

参见 [jimeng-model-catalog.md](jimeng-model-catalog.md) 的动态发现与验证机制。
