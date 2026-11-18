> Applicability: ONLY the six named 15-second regression fixtures. For any other task use V2.63; never inherit a fixture time or merger.

# V2.59｜Seedance 2 Fast 生产总控新增验收路由

当用户指定最终用途是“把提示词放进 Seedance 2 Fast 执行”，从源剧本自动推进至最终05，不应只交03、分镜节拍表、导演自评分数或“待用户继续要求优化”的报告。默认只让用户看完整可复制05和简短的证据边界。

- 01源事实/身份/原对白→03导演完整镜头与世界空间→内部比较合并/拆段方案→按实际入口可用生成时长构造Take时间轴与剪辑截取→05全要素视频提示词+必要POST_ONLY→生产静态校验→06独立脚本及人工QA→修复复跑→交付。
- V2.59必须使用新脚本 `tiger-video-prompt/scripts/audit_seedance2fast_v259.py` 和 `tiger-drama-qa/scripts/audit_seedance2fast_v259_independent.py`，带入来自独立03的 `--expected-shots`。V2.58脚本保留兼容历史旧格式，不能用于替代新验收。
- 模型入口时长未核实：使用官方API规格设计**候选**时间线，并标UI未验证；不得写“已提交成功”。视频素材未上传：复制块不得出现假的@引用。
- 有纯后期单元时，参与源镜头顺序和最终15秒总时长，但不用视频模型生成黑色无信息片段；文字贴图属于已有画面叠加，不重复加时长。
- 可复跑的六题15秒样例供回归，局部单镜头（如坠落抓前臂）仍允许。六个样例是用户对话提炼的短情境，不是批准的正式剧本/资产。
- 不声称Skill已安装、真实Seedance已生成或视频效果已过QA，除非有可核验实际操作证据。
