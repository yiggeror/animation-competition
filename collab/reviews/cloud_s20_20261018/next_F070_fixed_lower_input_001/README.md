# F070四输入短门：0次图像调用

先看 `complete_target_gray_REVIEW_ONLY.jpg` 和四张 `inputs/` 实图。第一图为新上身、双臂、掌腕及整裙的构图参考，独立完整下肢来自已通过067；这是绘制准备，不是生成成片。仅候选标签070，未冻结曝光。

1. `inputs/01_unique_complete_F070_fixed_lower_target_REVIEW_ONLY.png`：唯一完整目标。
2. `inputs/02_same_pose_dual_clamps_X_3x.png`：同姿双掌及X；R→T_H、L→T_S，T_S在前，远R不夹第二杆。
3. `inputs/03_067_identity_head_clothes_shoes_patches_only.png`：067头颈、服装、鞋的局部参考，无旧整身或拳姿。
4. `inputs/04_new_upper_whole_skirt_white_full_legs_black_mask.png`：白为完整头颈、躯干、双臂手、整裙、T杆及必要隐藏根部重叠；黑为裸露整腿、鞋、奶奶。沿自然裙摆遮挡分界。

`fixed_complete_lower_067_roots_legs_shoes.png` 是从隐藏根部到双鞋的独立保留层；隐藏远根用同腿肤色补足，裸露下肢恢复为通过067的原RGBA。下肢不变形，y736以后支撑区与067逐像素一致。正常尺寸边界见 `under_hem_target_left_mask_right_boundary_1x.png`（左目标／右真实mask）。

提示词、拟用实参、来源及四输入SHA见相邻文件。未提交图像工具，未授权生成；等待Astra四输入短门。
