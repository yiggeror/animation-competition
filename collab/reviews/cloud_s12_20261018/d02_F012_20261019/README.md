# S12 F012 · 唯一一次原生绘图，蓝衫颜色门未过，交Astra复审

按Astra已双审的三输入与完整修订prompt，只执行 **F012一张、一次调用**；本线程先核0在途，当前仍0在途。018/022/026/030未调用。本包直接交未经任何修色/裁切/变形/清边的原始输出，不以局部通过称锁稿。

- [原生F012原件](originals/F012_raw_call01.png)，1024×1536 RGBA，SHA256 **`52c6faf1e5eda14c2930ca557b5d1624a4dea86853f8dd631dd950b7b0d89f2c`**，逐字节等于工具保存的 `/workspace/generated_images/exec-4ed0040a-88ad-458e-8527-ba4e6d7b7cfe.png`，工具原件仍在。
- [实际完整prompt](provenance/F012_prompt_approved_full.txt)，SHA256 **`c6477cb1d6eba61279e725314f92a5ac50fc00a40a1816abf6ef0bcdb43e4f89`**，与Astra指定完整SHA完全相同；[实际request](provenance/imagegen_request.json) 内prompt逐字相同。
- 输入顺序与字节保持已批f1564c2三输入：锁母95f80f2d…ed793、原03 ab88b69f…2b1671、F012施工图8b15409c…e912d；各完整SHA和路径见 [调用台账](provenance/generation_ledger.json)。修订只明确03来源优先级、未来G_FINAL与F012空掌G参考及“本帧不得握杆”，未加减改写批准原文。

## 实际看图与留隙

[母/F012灰底与深底全身](qa/00_full_native_mother_F012_gray_dark.jpg)、[完整远臂与双手2倍](qa/01_whole_far_arm_and_both_hands_actual2x.jpg)、[细发/眼镜2倍](qa/03_fine_hair_glasses_actual2x.jpg)已实际打开检查。远左袖口—肘—前臂—腕—掌随接近向前下走，近右仍空，单镯在远左，两鞋及跪坐完整；没有画入杆、鹤、箱或图中文字。没有从旧图贴移孤立的手。

注册保持 `.70+(275,112)`，不做额外对齐变形。[原生真画叠固定杆轴诊断](qa/02_registered_rod_clearance_DIAGNOSTIC.jpg)、[双手留隙3倍](qa/02b_both_hands_rod_gap_DIAGNOSTIC3x.jpg)使用实际原生像素与已批固定代码杆的投影端点/7px外描边，**是测量诊断，不是新场景Canvas**。全选区手部皮肤核最近距离，并扣半个原生像素对角线作保守余量：

| 实际手 | 到上签 neck3 外缘 | 到下签 body 外缘 |
|---|---:|---:|
| 远左 | 33.27 场景px | 49.43 场景px |
| 近右 | 46.32 场景px | 59.12 场景px |

实看两手指与杆确有空气间隙，未提前拇触或闭握；没有移动代码杆或鹤。生成是整张重画，非活动部位不保证逐像素等于母稿，未把同注册称为原像素不动。

## 母色门：蓝衫R通道失败，原件未修

按完整物理材质区域分别选区，蓝色排除白花/黑线，保留大片真实蓝色明暗；不是全图平均或只选安全小core。实际选区PNG在 `qa/masks/`，对应[皮肤](qa/skin_same_material_masks_actual.jpg)、[蓝衫](qa/blouse_blue_same_material_masks_actual.jpg)、[头发](qa/hair_same_material_masks_actual.jpg)、[裤子](qa/trousers_same_material_masks_actual.jpg)可复核。肤/蓝采用母包原同材质判据；因远臂移动仅新画皮肤包络随实际轮廓扩展，衣/发/裤物理区域不择色缩小。

| 材质 | F012−锁母均值Δ(R,G,B) | ±4门 |
|---|---|---|
| 皮肤 | (+3.11,+1.57,+0.50) | 通过 |
| 蓝衫 | **(+5.81,+1.83,+1.17)** | **R未过** |
| 头发 | (+3.03,+2.72,+3.40) | 通过 |
| 裤子 | (+2.87,+2.40,+3.38) | 通过 |

蓝衫完整选择约119091px（母118656px），R偏高5.81，不能签全材质通过。未执行任何自动全图调色、语义mask修色或第二次生图；是否沿同raw修色由Astra下一步处置。完整数值/选区方法/留隙见 [实际验证JSON](qa/actual_native_validation.json)，复现脚本 [tools/review_native.py](tools/review_native.py)。

原生alpha≥8实体bbox `[26,334,1000,1313)`，右端完整，最右约24px余量；alpha1bbox `[0,62,1004,1516)` 仍有远离实体的极低alpha，未擅自清理以保原始输出。细发镜框已实看，未拿统一alpha阈值抹细线。最终原生颜色/轮廓与动作仍交Astra双审，未签锁F012。

[授权来源](provenance/astra_F012_authorization.md)、[工具返回完整提示/原件指向](provenance/tool_response_preserved.json)、[完整总校验和](SHA256SUMS.txt)。本轮1调用/1原件，累计S12原生4次；0新场景渲染、0后态、0S24重渲。仅新增本独占目录，未改锁母、参考冻结包、共享实现/留言/ready/EDL/音轨或主分支。未使用Blender或新付费API。
