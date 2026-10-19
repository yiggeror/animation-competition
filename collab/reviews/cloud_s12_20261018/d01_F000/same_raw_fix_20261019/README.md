# S12 F000 · 同第3原件零生成修正，交Astra锁母复审

按 [Astra本轮批准原文](provenance/astra_zero_generation_repair_authorization.md)，保留41cb60c第3稿身份、跪坐、双手空起势及本帧机位。本轮 **0生图、0新姿态**。原3份生成原件/完整prompt与累计3调用沿父包保留；没有更改源原件。[本轮台账](provenance/repair_ledger.json)。

## 唯一候选与实际对照

- [修后原生F000](candidate/F000.png)，1024×1536 RGBA，SHA256 `95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793`。源第3原件SHA仍 `87f85597246e995ad4988b3a766c4f4171201851780e8c8ab5b3b0a93bf3cd61`。
- [原稿/修后灰深底对照](qa/00_native_before_after_gray_dark.jpg)，已实看细发、镜框、衣纹、双手与两鞋。
- [修后真实Canvas F000](actual_scene/F000_Canvas.png)、[同F000实际前后](actual_scene/00_same_F000_before_after_actual.jpg)、[肤色/蓝衫局部](actual_scene/01_face_arms_cloth_colour_actual.jpg)、[鹤腹压布5倍局部](actual_scene/02_belly_pressure_contact_actual5x.jpg)、[膝胫鞋同态局部](actual_scene/03_knees_shins_shoes_same_pose_actual.jpg)。附 [单帧静音MP4](actual_scene/S12_F000_same_raw_fix_scene1_1920x1080_24fps.mp4) 与完整解码PNG。

## 材质、线稿与清边

只在明确的皮肤/蓝衫区域内修色；[03肤色同材质选区](qa/source03_skin_selection.jpg)、[03蓝衫选区](qa/source03_blouse_blue_selection.jpg)与全部source/edit/core mask在 `masks/`，定义见 [源与区域](qa/source_and_region_definitions.json)。没有全图调色。按像素材质和局部保护mask，保留形体明暗斜率；黑线、深色细折、白花边界保护，编辑域内2px过渡。

最终对照03同材质区，**完整原始pigment选择区**（包含保护边缘）肤色各通道均值差为(−2.05,−3.78,−3.26)，蓝衫为(−3.42,−3.32,−3.17)，全部≤4。安全填色core最大差<2。不是拿缩小后的整图平均凑数。见 [最终完整材质统计](qa/actual_delivery_verification.json) 与 [修色保护证明](qa/material_alpha_verification.json)。裤色宽保护域、头发core、黑线/白花保护域RGB逐像素不变；alpha≥8全部逐像素不变。

仅清掉轮廓外6,223个游离alpha1–3像素；原RGB保留，alpha改0。距alpha≥8实体3px内的抗锯齿保留，头部暗细线额外保护至12px，细发与镜框保护alpha不动。[清除mask](masks/removed_low_alpha.png)、[RGB变化mask](masks/changed_RGB.png)、[清边后真实alpha范围](qa/cleaned_native_alpha_diagnostics.json)齐。核心轮廓、姿态和所有几何位置不改变。

## 只补压布接触，同场景核对

继续原55°平面、原关节鹤与双签靠左沿；箱体/盖/前板、.70+(275,112)人物注册、灯光、相机、六接触影函数和图均保留原字节。仅在原蓝布范围内加鹤腹旁小凹折及1.5px贴合暗线，放在鹤片后方。实际Canvas对比：右侧只411像素改变，范围x1450–1546/y786–797；箱前板y≥800逐像素相同。除注册后的原生变化区与这一小布折外，整幅实际Canvas差异为0。见 [实际变化mask](masks/actual_cloth_contact_change.png)。

最终单帧1920×1080/24fps/无声，原始Canvas SHA与浏览器审计相同；MP4解码MSE=8.520247395833334。工具/源Git版本与19个运行输入核对齐，[实际验证](qa/actual_delivery_verification.json)、[ffprobe](qa/actual_ffprobe.json)、[完整网络](qa/actual_canvas_network_events.jsonl)保留。0pageerror/0requestfailed；favicon404按实际console location记录，不称全资源200。

本轮两次同F000实渲：首轮完整材质统计有两个通道刚超4，原保护mask内微调1级后复核；首轮记录在 `qa/iteration01_full_material_borderline/`。最终只交当前候选，复现脚本在 `tools/`。没有调用生成工具或改变人物姿态。

**交Astra最终锁母，未放后态。** 未改共享生产源、Opus留言、EDL、音轨、ready或S24九图；未启动全片/Blender/付费API。
