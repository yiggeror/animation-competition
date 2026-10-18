# S13 d11–d13 闭口后起转小组 · 待 Astra 回审

**3请求 / 3原件 / 3原生采用图**，沿已锁d10→d11收口过程→d12明确闭口且保持头向→d13整头首转。[明确授权门](../provenance/astra_d08_d10_lock_and_d11_d13_gate.md)

优先看 [同尺度四态](qa/00_d10_d13_same_scale_actual.jpg)、[闭口/颌颈近图](qa/01_closure_before_turn_actual.jpg)、[三底](qa/all_three_on_three_backgrounds.jpg)。作者已实看：d11仅余小口缝，右向头角保持；d12嘴完全闭合，无口腔或舌，保持头向；d13闭口整头向近正面转，颅耳、刘海、两边发根/马尾及颈面一起变化，尚未完成向左扭开。三张眼睛逐渐睁到困倦细缝，手均画外，无手嘴接触；三底未见明显alpha块雾。

| 起帧 / 停 | 唯一采用图 | SHA256 |
|---|---|---|
| F078 / 6 | `approved_local/F078_d11_near_closed.png` | `65414abf51e5332d60519d47ca8a41fdc12d3c3b279183765c8030df8f39838b` |
| F084 / 3 | `approved_local/F084_d12_closed_before_turn.png` | `86c9623ef72008bbbd1bc6730c7f3b99c6a08fdfa05443c4ff73bb5a3b886b73` |
| F087 / 3 | `approved_local/F087_d13_whole_head_turn_start.png` | `29418e08e7b0285fb8690add34878d600532c8a1d39f55379a915ffbca570660` |

三图1024×1536 RGBA，与各自工具raw逐字节相同；无本地重绘、嘴贴拉伸、warp或alpha过滤。沿用画层注册`.85+(330,−30)`，不重复套d01早先缩放。前十张已锁画稿不改，本组`approved_local`仅作者自审待Astra。

[0–89f隔离画层](qa/isolated_90f_through_d13.mp4) 为1280×720、24fps、90帧、无声中性底。已独立解码 [F068–089边界帧](qa/decoded_68_89_exposure_contact.jpg)，核78×6 / 84×3 / 87×3，F084–086先闭口、F087才转；数据见[验证JSON](qa/exposure_90f_validation.json)。**这是PNG画层曝光，不是Canvas接景或完整S13通过。**

根目录构造参考同步最新顺序：d11/d12保持+24°右向、d13才转向+8°；角度为设计值，未冒称成图精确角。仅调整这三态构造与状态说明，120f/16态、F100尾落定不变。

`requests/call_013/014/015_request.json`保留完整实际提示词/参数；配套response记录实际输入与原图SHA、默认工具原件路径，`*_tool_return_metadata.json`保留完整返回提示。`originals/`原件与工具默认路径均保全，图像模型版本未返回。三个`qa/dNN_validation.json`及`tools/adopt.py`可核原生采用与依赖，`tools/build_qa.py`仅重建核验、不调用图像服务。

[整包验证结果](qa/delivery_validation.json)核前十锁图不变、新三图与raw/默认工具原件一致、来源链、曝光及图像解码；复核入口`python3 collab/reviews/cloud_s13_20261018/d11_d13_group/tools/validate_delivery.py`。语义结构仍以实际视觉审查为准。

本组无追加修复/退回；累计15请求、15原件、13采用姿态、先前2未采用原件保留。未开d14，未写S13模块或接景，未改共享实现、EDL、音频、留言或ready。
