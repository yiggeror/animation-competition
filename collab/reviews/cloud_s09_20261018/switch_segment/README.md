# S09 开关小段 · 交 Astra 复核

本轮原生图像工具 **3 次请求、3 张返回原件**，对应 d02/F008 预推、d03/F014 推 ON 不亮、d04/F018 等待不亮。F000 沿用 Astra 锁定的 `1bbdc358` 原图，本轮重生 0 次；仅去除 5652 个 alpha=1 的透明噪点，RGB 和 alpha>1 均不变。累计原生调用 4 次、原件 4 张。

- [实际编码小段](qa/S09_F000-F025_drawings_only.mp4)：26 帧、24fps、1280×720，F000–F025；[实际解码接触表](qa/actual_encoded_frames.png)、[曝光表](exposure_segment.json)。已编码并解码全部 26 帧，只有画稿层和中性底，无音频。
- [四态对照](qa/switch_4states_contact.png)；三态注册稿为 `candidates/d02_registered.png`、`d03_registered.png`、`d04_registered.png`，1536×864 RGBA。
- 原件在 `originals/`；完整提示词、实际调用参数及含原始 data URL 的完整返回在 `requests/`；逐态蒙版、像素检查和局部前后图在 `masks/`、`qa/`。来源与复核摘要见 [verification.json](qa/verification.json)。

新锁定手电轴长约 **240.21px / .961H**，中心约 (896.13,461.62)，旧 175px 目标已被替代。所有候选沿用同一整体注册。最终腰上裁框为注册画布 `[280,80,1304,656]`，再等比放至 1280×720；裙摆原图截线约 y676，位于裁框下缘之外约 20px。

d02/d03 仅合成原生输出中的拇指/开关局部，d04 仅取原生眉区；蒙版为 0 的区域逐像素沿用上一态。d03 原件宽 1671，合成时仅右侧透明补 1px，原件未修改、未缩放。作者与云端 6.1sol 已实看，未见明确阻断；d03 滑块端点部分被拇指遮挡，不能宣称 ON 机械端点已完全可见验证。最终采用仍由 Astra 决定。

后续两击仅交 [新筒长局部参考](../contact_reference_v3/README.md)，尚无触掌画稿。F026 退 OFF 后需复核实际握姿，再按新参考审全臂、五指、尾盖先到与两次离掌。
