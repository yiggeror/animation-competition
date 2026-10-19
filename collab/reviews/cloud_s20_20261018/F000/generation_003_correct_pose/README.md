# S20 F000 call003：正确臂链原件＋冻结白域回贴候选

按Astra主/独审通过的 `3f1cb1e644f87c689e1931dcf69a5bea76b6a952` 四输入和完整prompt，**原样执行唯一一次**。本轮1调用、1原件、0重试、当前0在途；本云S20累计3调用/3原件，后态0调用。旧坏臂完整原件没有送入本次模型参考。

本次原件实际为 **1672×941**；近L从近肩/近袖经肘接高位镯掌，远R按已审遮挡从躯干后接低位裸腕。完成实际臂链与尺寸检查后，只按冻结白域回贴。**交付为待Astra审查候选，不据保护点零差签成品。**

## 原件、候选和实际看图

- [唯一call003原始PNG](S20_F000_call003_correct_pose_raw.png)：SHA256 `6eb8ed6145da4cf9a053993c383ae66f80b474d1a4f8b131a89cfd9e3fd6b204`。原工具文件 `/workspace/generated_images/exec-d99fd606-c9c5-4b33-979b-1c8a66718951.png` 保留，交付副本与完整工具返回中的载荷原字节相同。
- [冻结白域回贴候选](S20_F000_call003_white_composite_candidate.png)：SHA256 `8d628e5fa1d5c8d69aaea749c37cd2b9b1fe14b971d6b38f8efa4a37f8add433`。白域39,395像素从本次raw直接取RGBA，其余全部取call001原像素；实际改变38,901像素。
- [target／实际原件／回贴候选并排](qa/target_raw_composite_comparison.png)、[全身灰底](qa/composite_full_gray_QA.png)。
- [近L肩袖至肘](qa/composite_near_L_sleeve_elbow_4x_QA.png)、[近L腕镯接回](qa/composite_near_L_wrist_jade_4x_QA.png)、[远R低腕接回](qa/composite_far_R_wrist_seam_4x_QA.png)、[实际双掌四杆接触](qa/composite_rod_contacts_4x_QA.png)。

实际图形检查：近袖有布边厚度，近肘与斜上前臂连续；低位远前臂从躯干左缘接出，没有再保留call001的整条错误臂链或增添重复整臂。远上臂/肘依原target被躯干遮挡，检查可见连接与遮挡一致，不冒称测得隐藏3D关节。

**保留给Astra的局部复核点**：[镯下腕外原源／本次raw／候选放大](qa/wrist_outer_edge_source_raw_composite_QA.png)可见掌缘接回的小尖角及极浅细尾；[像素取样](wrist_edge_observations.json)记录本次raw已有的alpha1–4样点。本轮没有扩白域、改保护掌或清理alpha。其余颈色、主体外孤立alpha及CAM20/偶端接景也未处理/未核，后态未开。

## 完整请求与哈希

| 档案 | SHA256 |
|---|---|
| [完整实际提交档案](request_submitted.json) | `f10d3519bc3ca4b23b47ab79ae5d982daa2f794b8fd9fe4ec6b47670dd5463b1` |
| [实际工具参数JSON](tool_args_exact.json) | `a7256e8c0f94b47be638a6d560c03b65b1440197b5c083cc578885caf0490710` |

以上为保存的UTF8档案字节哈希，不冒称传输层字节哈希。实际工具参数与冻结准备请求的`args`逐项相同。其他档案哈希见[请求哈希索引](request_artifact_hashes.json)。

[完整prompt](prompt_zh.txt)、[原冻结准备请求](frozen_gate_request_prepared.json)、[原冻结四输入清单](frozen_gate_input_manifest.json)、[四个实际输入快照/SHA/路径](submitted_input_snapshots.json)、[完整原始工具返回](tool_return_original.json)、[Astra授权原文](authorization.json)、[0在途前检](preflight.json)、[当前单次状态](status.json)均保留。模型工具为`image_gen.imagegen`，底层模型版本未披露。

PNG IHDR和Pillow均读得1672×941，见[尺寸实测](dimension_inspection.json)。原件未缩放、补列、裁切、改色或清alpha；候选也没有上述变换，仅作显式白域原像素选择。孩子、两掌、镯、四前杆、奶奶头颈与腰腿由call001保护原像素保持，原216帧和切点不动。

## 验证与复现

[实际看图记录](author_visual_review.json)、[白域像素验证](composite_pixel_verification.json)、[总验证](verification.json)、[本门SHA清单](SHA256SUMS.txt)齐。回贴方法见[完整处理脚本](compose_candidate.py)；它先检查原件尺寸与源/白域哈希，再逐像素选择，无额外修画。

```bash
python collab/reviews/cloud_s20_20261018/F000/generation_003_correct_pose/compose_candidate.py
```

脚本只处理本地已返回原件及QA，不调用模型、不渲场景。本门仅新增独占审查目录，所有旧门、旧原件、生产代码、EDL/声音、共享留言及ready原字节保留。

当前状态：**原件拓扑/尺寸观察通过；回贴候选待Astra审查腕缘，不登记最终成品。**
