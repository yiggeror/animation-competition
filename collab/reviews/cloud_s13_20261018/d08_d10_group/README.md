# S13 d08–d10 峰态小组 · Astra 已锁

当前状态：Astra 已实审并锁定本组三张（`9ed9d4fe`）；以下保留当时交付记录，三采用PNG未改。新闭口/起转组看 [d11–d13](../d11_d13_group/README.md)。

**3请求 / 3原件 / 3原生采用图**，沿合格d07→d08峰→d09独立续气→d10收束。d08为新call010，输入合格d07 SHA `93ca7ffb…7fff`，没有复用或改名失败call008。[授权原文](../provenance/astra_d05_d07_lock_and_d08_d10_gate.md)

优先看 [同尺度四态](qa/00_d07_d10_same_scale_actual.jpg)、[下颌/颈领/胸肩近图](qa/01_jaw_neck_chest_progression.jpg)、[三底](qa/all_three_on_three_backgrounds.jpg)。作者实看：峰态颅体无明显膨胀，张口随头颈后仰和胸肩吸气；d09下颌/胸肩略回，不是同图缩嘴；d10口与下颌收回、头颈前返、胸肩同落，眼仅细缝初开。d08/d09全闭无残瞳。角度/开口数值是手绘控制目标，不冒称精确实测。

| 起帧 / 停 | 唯一采用图 | SHA256 |
|---|---|---|
| F050 / 8 | `approved_local/F050_d08_yawn_peak.png` | `f14a522b0bd007ced18ab37fb0abaa25cfdca37a31309bc4c7271091d130c897` |
| F058 / 10 | `approved_local/F058_d09_sustained_breath.png` | `689689322eed3ef9999754de862eab47190de7c177432a747caf271d52236a4d` |
| F068 / 10 | `approved_local/F068_d10_yawn_release.png` | `b64b67f0262596c1dc150f71b9dce05e14aa12589a8214f2cc4612dd685a00be` |

三图1024×1536 RGBA，均与本组对应工具raw逐字节相同；无本地重绘、嘴贴拉伸、warp或alpha过滤。机位沿 `.85+(330,−30)`，不重复套d01早先缩放。`approved_local`仅作者自审，待小组回审；前七张已锁图不改。

[0–77f隔离画层](qa/isolated_78f_through_d10.mp4) 为1280×720、24fps、78帧、无声中性底。已独立解码 [F044–077边界帧](qa/decoded_44_77_exposure_contact.jpg)，核50×8 / 58×10 / 68×10，F077仍d10；证据在 `qa/exposure_78f_validation.json`。**这是PNG画层曝光，不是Canvas接景或完整S13通过。**

`requests/call_010/011/012_request.json`保留完整实际提示词/参数；配套response记录输入与原图SHA、工具原件路径，`*_tool_return_metadata.json`保留完整返回提示。`originals/`原件与默认工具路径均保全，图像模型版本未返回。三个`qa/dNN_validation.json`及`tools/adopt.py`可核原生采用与依赖；`tools/build_qa.py`仅重建检查，不调用图像服务。

本组无追加修复/退回；累计12请求、12原件、10采用姿态，先前2未采用原件仍保留。未开d11。120f/16态、F084闭口、F100尾落定保持；未改共享模块、EDL、音频、留言或ready。
