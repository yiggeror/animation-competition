# S24首F000 · 一次原生返回，待 Astra 锁母态

参考`035c998d`已协调+独审冻结；本轮依[首张一次授权](../provenance/astra_reference_freeze_and_first_F000_gate.md)只调用一次`image_gen.imagegen`，没有F006或后八张，没有追加修复调用。

唯一候选：[F000_native_rgba.png](candidates/F000_native_rgba.png)，1024×1536 RGBA。SHA256 `35bb55ead65abf20e3862b4d66dde2f0ed25023f31fb634fa2f03bcda0c72281`。它与[raw原件](originals/S24_F000_call_001_raw.png)及默认工具路径逐字节相同，无本地重绘、搬脸、warp、修色或alpha过滤。

已实际查看[三底](qa/00_raw_three_backgrounds.jpg)、[固定母稿/候选同画布](qa/01_master_and_candidate_same_canvas.jpg)、[完整颏颈领](qa/02_jaw_neck_collar_actual.jpg)。作者观察：眼睛清醒，鼻/视线朝左下，嘴为闭合中性线、尚未得意；两条辫尾短垂，未沿困眼/水平大尾。完整颏、耳后、颈面、领口连接可读，手肘在画外；三底未见明显块雾。真实母态结构/身份仍由Astra锁定。

**裁切待锁：**实际原件的头位比构造提案偏低，不能直接声称原注册通过。[中性底A/B配准比较](qa/03_registration_candidates_neutral_NOT_SCENE.jpg)及[参数JSON](candidates/registration_candidates.json)保留A=`.67+(600,90)`原提案、B=`.70+(590,20)`整层候选。B把可见发顶提到更接近原景，但头高比构造略大；两者均未冻结。原生PNG未改，比较图只是整层等比/平移诊断，**不是Canvas接景或整镜实片**。

[同语义区域色对照](qa/04_semantic_color_comparison.jpg)及[ROI统计](qa/semantic_color_comparison.json)对固定母稿91715601…850分别取内区：候选中位数ΔRGB为头发`[+6,+5,+6]`、皮肤`[+2,+4,+3]`、裙黄`[+2,+2,0]`、领白`[+1,+2,+2]`。头发略浅及其余小差交Astra判断区域色基，不以全图均值或自动阈值冒称完全同色；没有擅自修色。

完整实际prompt/参数/三个输入SHA在[request](requests/call_001_request.json)，[response](requests/call_001_response.json)记默认原件路径及返回SHA，[工具元数据](requests/call_001_tool_return_metadata.json)保留完整返回提示。默认原件仍在`/workspace/generated_images/exec-442f4faf-84e6-4c96-b9af-02582c9c01aa.png`；工具未返回模型版本，未猜型号。`tools/inspect_first.py`仅重建诊断，不生成或修改人物。

9态60帧时表未变；仅候选，不登记ready，不改生产模块/EDL/音频，不并发触碰S13修色。下一门为首F000的颏颈体积、裁切/配准、身份和区域色基锁定。
