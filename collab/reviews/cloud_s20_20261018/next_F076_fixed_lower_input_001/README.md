# F076零调用四输入：待Astra短门

先看 `complete_target_gray_REVIEW_ONLY.jpg`、`contacts_1x_REVIEW_ONLY.png`、`under_hem_target_left_mask_right_boundary_1x.png`。仅施工参考，未生成原生新画；076仅单态候选标签，不安排曝光或后态。

1. `inputs/01_unique_complete_F076_target_REVIEW_ONLY.png`：完整目标。沿070→073继续头颈胸盆、肩肘带腕；远臂自然屈肘，施工关节点的上臂/前臂长度保持，两臂分开、不互绕。新上身、掌腕、整裙与两T杆作为连续参考组件变化，固定原位完整下肢。
2. `inputs/02_same_pose_dual_clamps_X_3x.png`：同姿双掌/X。R→T_H、L→T_S，T_S在前经过远卷指，X在掌前；不让远R夹第二杆。X约(369.218,404.581)，交角77.629°，仍属第一次绞签末部。
3. `inputs/03_073_identity_head_clothes_shoes_patches_only.png`：已过073身份、衣料、鞋局部；无旧整身或拳姿。
4. `inputs/04_complete_upper_whole_skirt_white_full_legs_black_mask.png`：新头颈、躯干、两完整手臂掌腕、整裙、T杆及隐蔽根部重叠白；裸露完整腿鞋黑，边界沿自然裙摆遮挡。

已过的完整皮肤腿鞋/隐蔽根部层和原C杆层直接原字节复制，SHA不变；奶奶锁定。固定支持、奶奶及可见C杆RGBA变化0。没有新增腿根修补、拉伸前臂或移动膝踝鞋。

来源、四图SHA、骨长参考与提示词实参均随包。0新图像调用，未提交、未授权生成，先交Astra输入门。后续原件若仅整体构图漂移，按已过070原则统一相似注册完整新组件后再接回。
