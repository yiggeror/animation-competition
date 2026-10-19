# 当前进度：F000单姿态首母候选已实际接景，未锁稿

Astra已批准09c6三关键结构与55°初鹤斜靠布，批准原文见 [F000来源](d01_F000/provenance/astra_F000_authorization.md)。只做F000一姿态，三次同态原生/局修及完整提示词、实际一帧场景齐于 [d01_F000/README.md](d01_F000/README.md)。颜色对03尚未签一致，实际等比注册也待Astra冻结；不派生后态。下文保留09c6参考阶段的历史记录，构造图仍不是人物画稿。

---

# S12 · 三关键体量与192帧曝光参考，待Astra冻结

独占分支`cloud/s12-reference-20261018`，只交本目录。已读取并实看旧anim_12/g12、三视03/04，复核当前清单、script-v3第4场、EDL和S12代码；冻结源aa397e44887e47d395b699fdba92cbd7795a9001，末次远端复核六项关键源仍相同。S12为8秒/192帧，当前EDL49.583333–57.583333秒，未改EDL或声音。

先看[三关键总览](reference/04_three_key_overview.jpg)，再看大图[A/F000首态](reference/S12_A_F000_volume_contact.jpg)、[B/F064握双签](reference/S12_B_F064_volume_contact.jpg)、[C/F114举鹤](reference/S12_C_F114_volume_contact.jpg)。**人物灰体、骨线和手体块全部是构造参考，不是人物画稿、不能入片。** 鹤PNG仅为现有代码道具的真实独立光栅参考；本轮没有原生人物生图、没有实际场景片。

[实际身份/骨长测点](reference/00_actual_identity_and_bone_measurements.jpg)、[旧跪姿问题实图](reference/01_actual_old_kneeling_risk.jpg)保留原始参考像素。最新04已实看，但明确复审选择03为工作基准，04颈影未解决且肤色变浅；依据见source_manifest。03头高H=147原图px；人工投影量尺上臂约.843H、前臂.602H、手.368H、股/胫各.878H。衣下肩/髋/膝有±6–12px估计误差，不能当真人正交解剖数据。固定3D提案采用上臂.86H、前臂.64H、股.90H、胫.89H、胸髋1.43H，三态骨长不变，透视短缩不靠拉画。

[掌握点接触近图](reference/05_palm_grip_contact_construction.jpg)、[侧/顶视隐骨架](reference/06_side_top_hidden_structure.jpg)、[膝胫鞋背接地](reference/07_ground_contact_closeups.jpg)、[层次/箱沿/光接口](reference/08_layers_box_light_interface.jpg)分开交。近右无镯→body下签，远左玉镯→neck3上签；前臂保守表面间隔三态约59/96/104px，肘不堆叠。两掌点不是腕点；源码body[-75,6]、neck3[10,0]实际取点，双签恒长、遮挡杆段共线。首态未握杆端有箱沿支点，膝/胫/鞋背分接触影，原镜末段微推近的模型脚余量约16.3px。原画/真实指形及实景尚未验收。

[192帧拟排曝光CSV](exposure_192f_PROPOSAL.csv)与[时间图](reference/09_exposure_timeline_PROPOSAL.jpg)齐：0–64先左后右握；64–114整身回直举鹤；110约4.583秒见透光，120=5秒轻提；132后落定，末看画右画外小满。28行只排时点/拍点，**不宣称已构造28张姿态**。当前只有三个关键，未绘任何28图。慢动6f段若实际换张跳变，后续拆2–3f中间态、保持192f；不让代码单独插值道具撕开固定手掌。

[三关键数值/坐标](geometry/three_key_pose_proposal.json)、[原图测量CSV](geometry/actual_identity_measurements.csv)、[六接地域](geometry/contact_shadow_anchor_proposal.json)、[接景接口](geometry/scene_integration_interface_PROPOSAL.json)、[核验](qa/geometry_and_exposure_validation.json)可交画师和接景。空间只用H与场景像素，质量重心是明确权重假设的代理值，不冒称人体动力学证明。源和复现工具见provenance及tools。

**Astra本轮要确认的提案：**初鹤为收颈收腿、55°斜靠布，后转85°近立，替代旧squash压鹤；它与剧本“平放”的字面有差别。若必须完全平放，请先裁定箱内深度/折叠姿势。具体绘图门见[POSE_NOTES](POSE_NOTES.md)。参考/握点/注册和时序未冻结，不提前生母态，更不批量28图；通过后先1张首母，实看手/骨长/地影再小段续。

本轮图像工具调用0、人物新画0、完整场景/全片/Blender0、新收费API0。只在独占review提交，生产实现、Opus留言、共享文档/EDL/音轨/ready及S24九图未改。
