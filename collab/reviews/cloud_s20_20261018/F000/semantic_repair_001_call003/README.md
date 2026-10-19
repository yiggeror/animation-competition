# S20 call003：三语义片同raw修复，待短审

按Astra认可的call003双臂结构，仅修近L腕、远R短前臂和前襟。**本轮0模型调用、0新raw、0在途；后态未开。**

[修复候选PNG](S20_F000_call003_semantic_repair_candidate.png)，1672×941，SHA256：`423715194ffaa08e867a0e1e3c6f6febe5de703e6c84fb2dc26d282ab6139943`。

| 语义域 | 显式mask（白可修） | 实际前后对照 |
|---|---|---|
| 近L镯后腕 `[970,358,1018,410]`：扣真掌/镯，顺真腕接003前臂，清尖/浅尾 | [L腕mask](masks/01_near_L_wrist.png) | [放大对照](qa/near_L_before_after.png) |
| 远R `[974,416,1031,470]`：扣真掌/胸衣，整短前臂接肤色及上下缘 | [R前臂mask](masks/02_far_R_forearm.png) | [放大对照](qa/far_R_before_after.png) |
| 前襟 `[1018,398,1200,520]`：完整可见衣料片，扣两新臂/袖口/低腕/外轮廓 | [前襟mask](masks/03_visible_front_cloth.png) | [整片对照](qa/cloth_before_after.png) |

前襟上缘沿近臂遮挡，003提供上侧新衣；001仅贡献确认蓝白衣料的下侧同坐标纹理与折线，衣料源域与旧肤臂膨胀保护域交集为0。蓝布色带整片过渡，003真实折线剖面接通原断点；整组花朵保留，衣料mask内y505–519与001完全同像素，y520起不动。没有沿y469硬切，也没有拆成窄条交付。

[三mask接触表](qa/mask_contact_sheet.png)、[全身叠域](qa/three_semantic_masks_overlay.png)、[修后全身灰底](qa/repaired_full_gray.png)、[三域union](masks/all_three_semantic_union.png)、[域外保护图](masks/protect_outside_semantics.png)齐。三域外、真双掌/镯/四前杆和孩子RGBA零变。原R掌完整旧guard也零变；原L粗guard含获准返修的腕片，本次按[真L掌](masks/true_L_palm.png)和[真镯含墨线/AA](masks/true_jade_with_ink_AA.png)区分保护，没把腕片误算成掌本体。

全部源文件未改：[call003原raw](../generation_003_correct_pose/S20_F000_call003_correct_pose_raw.png)、[修前白域候选](../generation_003_correct_pose/S20_F000_call003_white_composite_candidate.png)、[001保护/下侧衣料源](../generation_001/S20_F000_call001_raw.png)。完整源SHA、颜色/边缘方法及花朵来源见[修复来源](repair_provenance.json)，[授权原文](authorization.json)、[作者实看](author_visual_review.json)、[验证](verification.json)、[SHA清单](SHA256SUMS.txt)保留。

[完整脚本](repair_semantic.py)只处理本地源像素。已在新临时目录只用上游输入重放，最终PNG及三mask逐字节一致，成品未作为重放输入；见[隔离重放验证](replay_verification.json)。复现命令：

```bash
python collab/reviews/cloud_s20_20261018/F000/semantic_repair_001_call003/repair_semantic.py
```

仅授权腕域做局部alpha边缘修复；颈色、全局/主体外alpha、机位/道具抓持、原216帧和切点不改，不渲场景、不登记ready。当前仅交mask与零调用候选，待Astra短审。
