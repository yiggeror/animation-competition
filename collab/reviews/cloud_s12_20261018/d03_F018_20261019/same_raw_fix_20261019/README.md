# S12 F018 同raw修复候选 · 零生图调用

[最终原生RGBA](candidate/F018.png) SHA256 **`c63f57f53bc2f4bbca59dba4310ea55c0629b354520f8d0becbe88f932ff40be`**。唯一生成原件仍在[父包](../originals/F018_raw_call01.png)，SHA `fbc502639b90de00eb0b664a41af7898df15e92bf5d58ac9e172579121b486a3`；完整prompt/request/返回元数据保留，原件未改。本修复新增图像调用0，S12历史累计仍5，022未开。[Astra授权原文](provenance/coordinator_authorization.txt)。

真实远肘体中心估计 **(770,836)**，见原件坐标格；完整前臂、玉镯、整掌与全部手指统一逆时针抬 **5°**。3.5°仅是起始试值，实含外AA的原生预检不足，按0.25°步进至5°后才渲。肘周u=−18…18原生px短过渡；其外单一刚体旋转，比例1、行列式1，完整逆映射误差≤1.14e−13px。没有单挪腕/拆指。肩袖及近臂几何不挪；外域RGBA保持原件。[映射及计数](provenance/source_mapping_and_counts.json)、[逐像素逆映射](provenance/inverse_geometry_map.npz)、脚本和显式mask齐。首次本地预检曾漏32个旧镯缘，补8px提取保护域后清净；均在实际渲染之前。919个腾空旧臂域alpha1–7残留随原轮廓清除，非全图清理。

[000/最终012/修018同尺度灰深底](qa/01_000_012_018_same_scale_gray_dark.jpg)、[完整臂/双手修前后2倍](qa/02_complete_arm_both_hands_before_after2x.jpg)、[三态布尖4倍](qa/03_000_012_018_tip_color4x.jpg)。冠发/髻只回明灰域；暗发、耳后、墨线和高光保原件。蓝衫分同平面只微降R约1.57–3级，G/B不动；布尖单独按最终012的明暗面正增益校准蓝与受影花纹，保护折线/外轮廓。受影蓝1374点、花瓣199点对最终012均值误差各通道≤0.13。亮面花芯仅11点，报告如实列出，不把小样本当整面材色通过。

| 固定000材色门 | 修018−000 RGB均值 | ±4 |
|---|---|---|
| 灰发 | +2.025, +2.552, +3.141 | 通过 |
| 蓝料 | +3.208, +1.951, +1.216 | 通过 |
| 裤色 | +0.698, -0.556, -0.163 | 通过 |
| 皮肤 | +3.102, +0.565, -1.258 | 通过 |

实际原机位 **F018 / t=.75** 只渲1帧：[无损Canvas](actual_scene/F018_canvas.png)、[一帧1080p24无声片](actual_scene/F018_oneframe_1920x1080_24fps.mp4)、[实际视频解码双手/真杆4倍](actual_scene/02_actual_both_hands_rods_decode4x.jpg)。Canvas SHA `46f97711aff0b9451ba72d5a413e4b42cfa6583853d9999657e12f80bb78f001`；MP4 SHA `24474e13069c77a88d992b19d868d8c7d8208c7f4914dfafdb8ce76106778003`，解码RGB MSE 8.523028。

按**实际注册人物和真实光栅杆所有alpha>0像素的单位像素方块边界**量空气，包含最外墨线/AA：远手上/下杆 **4.00 / 20.00 scene px**；近手 **42.54 / 56.08px**。[实际验证](qa/actual_scene_verification.json)。两手仍空；道具层PNG与最终012字节全同，六接地alpha域与源018原件全同，鹤仍布托。原机位、.70+(275,112)、箱布压折、55°鹤面、光/相机函数不变。[实际资源日志](qa/actual_canvas_network_events.jsonl)保真实URL/状态及favicon404，0pageerror/0requestfailed。

[实看记录](qa/author_actual_review.json)。当前交Astra复核的候选，未自签锁态；未渲019–021、未开022、未改共享实现/留言/ready/EDL/声音，仅交本目录至私有分支`cloud/s12-reference-20261018`。
