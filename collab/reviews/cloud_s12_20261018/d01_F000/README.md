# S12 F000 · 单姿态首母候选，未锁稿

沿09c6a981获批A构造和三视03，仅制作F000这一种姿态。**首母仍待Astra审原生体量/注册及对齐03色基，不能作为已锁母稿派生后态。** 一次首画、两次同F000局修，共3次工具调用/3份成功原件；没有生成其他曝光，没有开28图。

先看 [真实Canvas场景F000](actual_scene/F000_Canvas.png)、[已批A与实际解码并排](actual_scene/00_approved_A_vs_actual_F000.jpg)、[全膝胫鞋与接触影实图](actual_scene/01_actual_knees_shins_shoes_shadow.jpg)、[空手/签靠沿/鹤靠布实图](actual_scene/02_actual_empty_hands_rimsupport_cloth.jpg)。[当前原生候选](candidate/F000.png)是 [第3份原件](originals/F000_raw_attempt03.png)逐字节副本，SHA256 `87f85597246e995ad4988b3a766c4f4171201851780e8c8ab5b3b0a93bf3cd61`，没有程序重画人、变形、校色或改alpha。[灰/深底原生复核](qa/candidate_gray_dark_review.jpg)只作检查。

## 原件、输入与修正经过

[首次完整提示词](provenance/F000_prompt_full.txt)、[下肢修正提示词](provenance/F000_correction02_prompt_full.txt)、[同态手比例修正提示词](provenance/F000_correction03_prompt_full.txt)，各有完整工具request JSON、result元信息与 [调用台账](provenance/generation_ledger.json)。三份未经更改的PNG均在 `originals/`，工具保存于 `/workspace/generated_images/` 的原件也保留。第1份远鞋遮得过多，第2份两鞋补出但手偏长，第3份修手后进入本次接景候选；没有把失败稿抹掉，也不把3次调用说成1次。

身份只沿 [原03像素](inputs/identity03_original.png)（SHA `ab88b69f…b1671`），不用04变浅肤色。获批A的 [原生布局施工图](inputs/A_F000_native_layout_CONSTRUCTION_NOT_ART.png)明确是构造，不是人物画稿。实际工具输入及SHA见 [冻结记录](inputs/frozen_inputs.json) 和各request；[Astra批准原文](provenance/astra_F000_authorization.md)保留55°斜靠布、签靠沿、握后才举和首图接景条件。

## 实图观察与未过的门

已实看原生和真正场景解码：近右无镯、远左玉镯的袖—肘—腕—掌衔接，两前臂分开，两手未握；两条膝/胫/鞋链均入画。可见近膝胫与两鞋的接触影贴着原生轮廓。远膝/远胫地面接触自然被近腿遮住，不宣称六处都能独立看见。人工头高/臂/手测点与误差见 [量尺](qa/actual_native_landmark_estimates.json)，不能把宽裤下的隐藏髋膝踝当已证实的精确3D骨长。

初鹤用同一代码皮影、A的新关节姿态和真实55°平面投影，未用旧纵向squash。鹤身由箱内蓝布承托，两长签按新body/neck3端点靠箱沿支托，空手尚未碰签；F000不画透光色，箱盖内没有提前彩影。没有借旧G/groupM/action/rig的人物动作。

源箱、相机、房间和灯光保留；只对实际人物用等比注册 **.70+(275,112)**，替代参考阶段明确暂定的.75+(300,100)，不拉形或转整人。alpha≥8的真实轮廓在首帧有约50px底余量；同一个F000原生套末191相机的纯边界计算约20px，**不是末C成图/实渲证据**。极低alpha1的零散噪点仍原封保留，未签清边。具体见 [轮廓/六局部影mask/注册](qa/native_alpha_contacts_registration.json)；影mask只由同一原生alpha局部取样，未用整个人最低一行替全部接触点。

**颜色未过冻结门。** [材质core取样](qa/F000_material_baseline.json)与03中间色诊断的均值差，头发约(−4,−7,−8)、皮肤(−1,−10,−17)、蓝衫(−14,−15,−6)，裤子约(+3,+2,+3)。两边投影/明暗区域不同，这不是完整匹配语义区域的±4检验；但不能据此签既定色基一致。原生没有为凑数程序改色，`material_masks/`保留供后续准确对齐。当前值不得当已批准后态色基。Astra需先审姿态/实际注册和同raw色基/清边处理，再锁母稿；本包不续生成。

## 一帧实际渲染证据

独立 [F000唯一入口](scene/s12_F000_scene.js)只允许t∈[0,1/24)，拒绝后态。实际Chromium只渲1帧，1920×1080/24fps，附 [1帧静音MP4](actual_scene/S12_F000_scene1_1920x1080_24fps.mp4) 与真实解码。源PNG/审计SHA一致，编码RGB MSE=8.456987380981445；[验证](qa/actual_delivery_validation.json)、[ffprobe](qa/actual_ffprobe.json)、[运行输入清单](qa/F000_runtime_manifest.json)、[完整网络日志](qa/actual_canvas_network_events.jsonl)、[原始命令日志](qa/actual_canvas_command.log)齐。控制台404 location指向favicon；0pageerror/0requestfailed，未冒称全资源200。

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s12_20261018/d01_F000/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/cloud_s12_20261018/d01_F000/scene/s12_F000_scene.js build/S12_F000_scene1 --fps 24 --w 1920 --h 1080 --workers 1 --from 0 --to 0.041666666666666664 --mp4 build/S12_F000_scene1_1920x1080_24fps.mp4
```

人物原生像素未被代码改写。只在本独占review内交付；没有更改共享源码、Opus留言、EDL、音轨或ready，没有全192帧/全片/Blender/新付费API。
