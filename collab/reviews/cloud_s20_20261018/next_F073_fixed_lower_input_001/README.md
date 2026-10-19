# F073零调用四输入：待Astra短门

先看 `complete_target_gray_REVIEW_ONLY.jpg`、`contacts_1x_REVIEW_ONLY.png` 和 `under_hem_target_left_mask_right_boundary_1x.png`。本包仅绘制参考施工，不是原生新绘成片；073只是单态候选标签，未安排曝光。

1. `inputs/01_unique_complete_F073_target_REVIEW_ONLY.png`：唯一完整同姿目标，沿067→070继续肩肘带腕、远R左上、近L右下及头颈胸腰微前探；完整上身与整裙均变化，固定完整下肢、奶奶和原C杆。
2. `inputs/02_same_pose_dual_clamps_X_3x.png`：同姿双掌/X；R→T_H、L→T_S，X在双掌前，T_S从卷指前经过。保留完整原生卷指，没有让远R夹第二杆。
3. `inputs/03_070_identity_head_clothes_shoes_patches_only.png`：本次已过070的头颈、衣料和鞋局部，无旧整身或拳姿。
4. `inputs/04_new_upper_whole_skirt_white_full_legs_black_mask.png`：完整头颈、躯干、两条完整手臂掌腕、整裙、T杆和必要隐藏根部重叠为白域；裸露完整腿鞋、锁奶奶黑域，沿自然裙摆遮挡分界。

独立下肢为 `fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png`：同腿肤色清理旧衣残边与根部RGB蒙版，alpha与腿形不变，只含皮肤、腿鞋和隐蔽根部。根部局部可看 `fixed_lower_root_skin_only_3x.png`。目标中原已裸露的腿鞋恢复为通过070的原RGBA，双足支持和奶奶前景RGBA变化0；没有横截裸露腿、移动膝踝鞋或安排后态。

X约(395.954,401.240)，交角74.597°。完整提示词、拟用实参、来源和四图SHA见相邻文件。0次新图像调用，未提交、未授权生成，等待Astra实图短门。后续若仅整体取景漂移，先统一相似注册完整语义组件再判断接回。
