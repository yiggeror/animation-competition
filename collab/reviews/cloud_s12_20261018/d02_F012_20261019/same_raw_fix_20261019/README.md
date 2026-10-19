# S12 F012 · 同raw静态蓝衣R微修 + 真实单帧接景

依据 [Astra本轮批准](provenance/astra_same_raw_authorization.md)，只处理已保形的 `bbf19721fa2b183c8096578049518d5c292c2256` 唯一原件。**本轮0生图、0新姿态，018未启动。** 原件仍在父包 `../originals/F012_raw_call01.png`，SHA256 `52c6faf1e5eda14c2930ca557b5d1624a4dea86853f8dd631dd950b7b0d89f2c`，已核Git原字节不变。原始三输入、完整指定prompt及工具返回在父包保全，累计S12原生调用仍为4。

## 唯一修后原生与实际画面

- [修后F012](candidate/F012.png)，1024×1536 RGBA，SHA256 **`103ed4fb52c64b370560456ff0dde5a0820596ecfed9e28daee0f026aef7b4ff`**。
- [同尺锁母/原件/修后三图两底](qa/00_same_scale_three_native_gray_dark.jpg)、[五个物理分面](qa/01_physical_faces_same_scale.jpg)、[实际编辑/线折/白花/远袖保护图](qa/02_edit_and_protection_masks_actual.jpg)，已实看，不以全图平均代分面。
- [真实F012 Canvas](actual_scene/F012_Canvas.png)，1920×1080、绝对时间0.5秒；[单帧静音MP4](actual_scene/S12_F012_same_raw_fix_1920x1080_24fps_1frame.mp4)，24fps/1帧，SHA256 `0ee0c43ed478275f8c7c4d1fb676cd4e6bc019ad10aa3d69b700d6ca37260016`；[完整实际解码](actual_scene/F012_MP4_decoded.png)。Canvas SHA256 `ad478641b320c35cd7d083bc9b1184e77bbb65bb7ed51f7926fad88bc8ff5080`。
- [实际双手/双杆/层次3倍](actual_scene/01_actual_hands_rods_layers3x.jpg)、[膝胫鞋与接地2倍](actual_scene/02_actual_knees_shoes_ground2x.jpg)、[鹤压布实际4倍](actual_scene/03_actual_crane_cloth_contact4x.jpg)、[锁母F000与F012真实场景上下文](actual_scene/00_actual_F000_F012_context.jpg)。F000是旧实帧t0，F012是t0.5按原灯光函数采样，未把两者称同时间照明对比。

## 修色与清边边界

只在静态蓝色颜料内部，对近袖、背腰、下摆、领襟做软R减量（填色最大−4，2px编辑边界羽化）。完整蓝料明暗斜率保留，分区边界sigma6px平滑；暗墨/高对比折纹边与白花外缘保护，不做全图调色。活动远袖含保护外扩2px **RGBA逐像素不变**；所有G/B、皮肤/头发/裤子RGB逐像素等于同raw。所有alpha≥8逐像素不变，没有姿态/骨长/注册/缩放/轮廓变形。

只清11,527个距离alpha≥8实体超过3px的独立低alpha点（原值只有1/2/3），RGB保留；整个头发与镜框guard `[410,312,826,651)` alpha全保，远袖保护域alpha也不动，贴轮廓抗锯齿保留。清后alpha≥8 bbox仍 `[26,334,1000,1313)`；所有编辑/保护/清边mask在 `masks/`。见 [修正证明](qa/native_repair_verification.json) / [分区定义](qa/region_definitions.json)。

**整体蓝料均值已回±4内，仍有一个分面待裁定。** 下表按保存的完整物理分区测量，不只选择可安全编辑的小core。Astra原分区mask未随委托提供，本包显式保存了本地完整分区，数值不假称与Astra抽样定义完全相同。

| 本地完整分面 | 原raw相对锁母ΔR | 修后Δ(R,G,B) |
|---|---:|---|
| 近袖 | +6.47 | (+3.48,+2.30,+1.30) |
| 背腰 | +5.75 | (+2.68,+1.68,+1.18) |
| 下摆 | +6.09 | (+3.30,+2.20,+1.66) |
| 领襟含折影 | +7.77 | **(+5.86,+4.13,+2.77)** |
| 活动远袖，未动 | +3.03 | (+3.03,−0.48,−0.70) |

完整119091px蓝料选择ΔRGB由(+5.81,+1.83,+1.17)变为 **(+3.23,+1.83,+1.17)**。领襟完整分区仍含折影/保护边，未通过各通道±4；按授权没有扩大R减量超过4或改G/B，保其残余交Astra复核。**未以全蓝均值通过替代所有分面通过，未签锁F012。**

## 真实接景与层次证据

实际F012只渲一帧，采用原 `.70+(275,112)` 注册。原锁母场景中的箱/盖/前板、压布小折、鹤55°平面及根、双杆真实端点、灯光/相机/接地影变换函数逐段字节核相同，[源码等同性](qa/scene_source_equivalence.json)。六接地影改用**本张实际原生alpha**、保持原六接触区域及锚点；远膝/远胫自然遮挡，不称六处均独立可见。

实看真实Canvas：远左单镯整臂前下推进、近右仍空，两只手均未触杆；上签与下签分开、杆靠沿、鹤继续由布承托，未抬鹤。细发镜框、完整跪坐两鞋没有新增结构阻断，未见人物/杆穿插。

同时从成功渲染的浏览器**同一缓存图层**读回 [真实注册人物层](actual_scene/F012_person_registered_actual_layer.png)、[实际代码杆鹤层](actual_scene/F012_code_props_actual_layer.png)、[实际原生接地影层](actual_scene/F012_native_ground_shadows_actual_layer.png)，没有再次调用renderFrame。alpha≥8的实际人物/道具重叠像素为 **0**；按真实像素算远左/近右手到实际道具层最近距离约 **32.02 / 44.72 场景px**。这次有真实Canvas与图层，不只上一包示意叠杆图。

## 单帧命令与网络来源

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s12_20261018/d02_F012_20261019/same_raw_fix_20261019/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/cloud_s12_20261018/d02_F012_20261019/same_raw_fix_20261019/scene/s12_F012_scene.js build/S12_F012_same_raw_fix_scene1 --fps 24 --w 1920 --h 1080 --workers 1 --from 0.5 --to 0.5416666666666666 --mp4 collab/reviews/cloud_s12_20261018/d02_F012_20261019/same_raw_fix_20261019/actual_scene/S12_F012_same_raw_fix_1920x1080_24fps_1frame.mp4
```

[验证](qa/actual_delivery_verification.json) / [ffprobe](qa/actual_ffprobe.json) / [17个实际运行文件SHA](qa/actual_runtime_inputs.json) / [实际网络日志](qa/actual_canvas_network_events.jsonl) / [摘要](qa/actual_network_summary.json)。浏览器Canvas SHA与原PNG相同；视频解码MSE=8.379732。入口严格只开放F012，不借无画帧回退。

共有2次启动：初次独占入口几何相对路径写深一层，真实404 URL为 `http://127.0.0.1:42603/collab/reviews/geometry/three_key_pose_proposal.json`，**0帧输出**，完整失败记录在 `qa/failed_initial_geometry_path/`。修正并核所有相对路径后，1次成功输出F012、1次编码，没有重复已完成画面。成功轮0pageerror/0requestfailed，实际console另有 `http://127.0.0.1:33643/favicon.ico` 404位置，response事件未捕获该响应，不称全请求200。

[本轮台账](provenance/repair_ledger.json)、[总校验和](SHA256SUMS.txt)、复现脚本在 `tools/`。只新增本独占子目录，父包原件/提示/旧报告不覆盖；未改共享实现、留言、ready、EDL或音轨，未推共享主分支、未启动全片/Blender/付费API。待Astra审修后原生、领襟分面及实际F012；018继续关闭。
