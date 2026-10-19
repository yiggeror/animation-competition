# K02/F084明确峰姿：零调用四输入

峰姿由远肩抬起、远肘向身侧内收，近上臂更趋垂直而前臂趋平的完整骨链蓄力，加头胸腰配合达成，腕部保留随后反向回拧余量。

先看 `complete_target_gray_REVIEW_ONLY.jpg`、`contacts_1x_REVIEW_ONLY.png` 及 `076_passed_079_passed_084_target_same_canvas_upper_hands_1x.png`。三态从同画布固定裁区 `[235,125,865,720]` 直接取图，依次为076已过／079正确头颈已过／084目标，没有分别对齐。084可见肩肘腕收卷差别，交角保持约78.52°；峰姿不靠无限开角或延长手臂。

1. `inputs/01_unique_complete_F084_target_REVIEW_ONLY.png`：唯一完整峰姿施工目标，非新生成成片。
2. `inputs/02_same_pose_dual_clamps_X_3x.png`：同姿完整双掌/X，R→T_H、L→T_S，T_S在前。完整原生掌形和杆间遮挡一体保留，两条上臂/前臂骨长保持，前臂不相绕。
3. `inputs/03_079_identity_head_clothes_shoes_patches_only.png`：刚通过079的正确头颈、衣料和鞋局部，无旧整身或拳姿。头部仅整体反向微转2°，尺度1，不放大。
4. `inputs/04_complete_upper_whole_skirt_white_full_legs_black_mask.png`：完整新头颈、躯干、双臂掌腕、整裙/T杆和必要隐蔽根部重叠白；裸露完整腿鞋黑。

正常尺寸裙下边界见 `under_hem_target_left_mask_right_boundary_1x.png`。完整真实皮肤腿鞋/隐蔽根部、奶奶和原C杆仍锁定；固定层原字节不变，支持/奶奶/可见C杆RGBA变化0。来源、骨链、四图SHA与prepared prompt/实参随包。

0新图像调用，未提交或授权生成，未预排中间态、未采用、未冻结曝光；先交Astra图门。
