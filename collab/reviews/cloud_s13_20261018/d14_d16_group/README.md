# S13 d14–d16 尾三态 · 作者自审，待 Astra

**3请求 / 3原件 / 3原生整张采用**，沿锁定d13→d14继续整头转左→d15头到位、自由发尾向右滞后→d16发尾内收下落，F100落定。[明确授权](../provenance/astra_d11_d13_lock_and_tail_scene_gate.md)

已实看 [同尺度四态](qa/00_d13_d16_same_scale_actual.jpg)、[头/发根/自由尾近图](qa/01_d15_d16_head_root_and_free_tail.jpg)、[三底](qa/all_three_on_three_backgrounds.jpg)。全程闭口；耳、发根、颈面随整头转，d15/d16头和根基本稳，发尾单独完成余摆。没有面部搬移，三底未见明显alpha块雾。角度仅设计目标，不冒称精确成图角。

| 起帧 / 停 | 唯一采用图 | SHA256 |
|---|---|---|
| F090 / 4 | `approved_local/F090_d14_turn_left.png` | `8564d56395a8f4bceec62a3f3d9223c14daf6253f238cec37a485686cba3303d` |
| F094 / 6 | `approved_local/F094_d15_head_arrived_hair_lags.png` | `ad5c052f1a8a71ba21fdd6075428eec75e960038eaa932f1237e015519f0276d` |
| F100 / 20 | `approved_local/F100_d16_tail_settled.png` | `a38e44a702a7d4c1123dd4b6b8b6e2e749a22fb21762ef61ca0c7444f95c0069` |

三图1024×1536 RGBA，均与工具raw逐字节相同；无本地重绘、warp、镜像、嘴贴拉伸或alpha过滤。此前d01–d13锁图未改。本组`approved_local`仅作者自审，不代Astra终审。

`requests/call_016/017/018_request.json`保留完整实际提示词和参数；配套response、tool_return_metadata保存输入SHA、原图SHA及完整工具返回提示。`originals/`和默认工具原件路径均保留，图像模型版本未返回。每态验证和采用脚本在`qa/`、`tools/`。

[整包验证](qa/delivery_validation.json)核前13张锁图不变、新三图与原始工具输出一致、十六态时表、真实场景120帧对照及共享依赖未改。可运行`python3 collab/reviews/cloud_s13_20261018/d14_d16_group/tools/validate_delivery.py`复核。

本组无修复或退回；累计18请求/18原件、16采用姿态、先前2退回原件保全。时表保持120f/16态，F084先闭口、F087起转、F100尾落定。十六态已接[真实Canvas全镜候选](../full_scene/README.md)，未修改共享代码、音轨或ready。
