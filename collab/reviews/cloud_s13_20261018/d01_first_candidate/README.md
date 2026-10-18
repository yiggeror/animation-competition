# S13 d01 首张实图 · 已获 Astra 锁母态

最新状态：Astra已锁本页配准PNG `91715601ae81…82050`。授权与下游d02–d04交付见 [当前小段入口](../d02_d04_segment/README.md)。以下保留首图当时的交付、原件与配准过程，原文件不改。

本次只执行已放行的 **d01 / F000–017** 一态，实际 1 请求 / 1 原件 / 0 后续态。图像工具执行成功，原图 1024×1536 RGBA；输出已实际打开，并在正确 alpha 合成的浅底、深底、灰蓝底上检查。不是代码人物，也不是参考构造图。

## Astra 优先看

- [同机位实际像素静态预览](qa/registered_same_camera_neutral.jpg)：只有中性底，不是场景合成或 Canvas 自渲。
- [眼、耳颌、颈肤、领口近图](qa/eyes_jaw_neck_collar_actual.jpg)：左为原件，右为整张等比配准候选；没有局部拉脸或改颈。
- [配准候选三底](qa/registered_on_three_backgrounds.jpg)、[原图三底](qa/raw_on_three_backgrounds.jpg)。

我方静态自审：身份、刘海、双低马尾、红花、黄白点衣与白圆领延续参考；头向画右，双眼清醒，瞳孔偏右且略下，嘴小开，好奇而非假困；近耳—下颌—颈肤—领口及双肩袖没有明显断接。真实头形、颈面和衣领是画出的连续形体，没有照灰棒成图。实际转角和关节位置未作精确测量，不宣称达到字面35°/12°或逐点重合。当前仍需 Astra 判断是否锁为母态，**没有从这张继续派生 d02**。

初看裸 RGBA 显示似有软雾，正确三底合成已澄清：alpha=0 区有非零隐藏RGB，合成后没有大范围雾边。原alpha保留，没有阈值收紧、洗边或改发缘。原主体alpha以253/254为主，未强改成255；深底细发线的最终观感请沿本包三底实看，不从alpha极值判断坏图。

## 原件与唯一配准候选

| 文件 | 用途 | SHA256 |
|---|---|---|
| `originals/S13_d01_call_001_raw.png` | 工具原件，像素未改 | `31cb92ed5bee1e6776106b071dbf442f3815b0aa12e1e7077a61903bd4db413b` |
| `candidates/S13_d01_uniform_registered_rgba.png` | 整张等比配准候选，尚未锁 | `91715601ae814bd84a3dc8d6ce43f1cc809a7bdd74e7390fefffe579f6882050` |

原图工具保存路径 `/workspace/generated_images/exec-de4034dc-f783-4c59-81a1-bc96d1e05e51.png` 仍留原处，本包原件为逐字节副本。

按实际原图人工估计实心冠顶y216、下颏y904，H≈688px（选点误差约±4px，不计呆毛）。候选用**单一等比变换** `source'=raw×0.9302325581+(56.09302326,31.06976744)`，将H约置为640。没有对枕骨、颈根、双肩逐点拟合，不能把配准当解剖证明。之后继承 `shot=source'×.85+(330,−30)`。完整矩阵和限制在 [registration.json](candidates/registration.json)。

该缩放后源图下缘落到场景y≈1210.92，低于1080画幅底，故原图下胸截断线不会进入最终镜头。三底与近图只作质量检查；只有 `candidates/` 的RGBA是配准素材，不可将带字JPG接入。

## 请求及授权链

- 审查原文：[astra_first_gate.md](../provenance/astra_first_gate.md)。冻结的是首态参考，真实母态待本次审核。
- 实际完整请求：[call_001_request.json](requests/call_001_request.json)，输入路径 / SHA：[call_001_input_manifest.json](requests/call_001_input_manifest.json)。
- 工具返回元数据：[call_001_response.json](requests/call_001_response.json)；返回图像完整二进制即原件PNG，不在JSON重复大段base64。工具未返回模型版本，不猜图像模型名。
- 调用时使用的旧构造参考已另保全 `requests/input_snapshots/S13_d01_F000_construction_as_sent.png`，避免本轮“d01已冻”图中文字更新导致历史输入不可复核。
- 整张配准可用 `python3 collab/reviews/cloud_s13_20261018/d01_first_candidate/build_registration.py` 复现，不调用图像服务，不局部修画。

## 同包后段参考修订

F078仍为“即将收口”，不再误写已收口；**F084口高归零**，明确闭口后再扭开。尾端落定提案从F104提前F100，d15停6f、d16停20f，总120f不变。此修订只属后段参考，真实马尾是否吊住须后续实际曝光检查；必要可再提前F098，不用参考图冒充自然度通过。

当前d01已锁，d02眼先右上 → d03整头右转 → d04清醒收嘴已按新授权顺链自审交回；本页原件和配准PNG保持同SHA。未启动后15张独立抽图或整镜模块 / 场景渲片。
