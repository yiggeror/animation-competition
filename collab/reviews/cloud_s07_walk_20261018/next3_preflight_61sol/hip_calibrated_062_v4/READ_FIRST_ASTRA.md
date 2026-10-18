# S07 F062：实际预摆、连续绘制区与保护域快审

本次只推进 S07 F062。先交这一态输入门，Astra 审定后再真实生成062；068/073沿合格062顺链，未启动。本包新增图像请求0，不是成品画稿。

请先看三张：

1. [057真实源／062实际预摆／髋膝踝代理](qa/F057_F062_actual_pixels_and_chain_comparison.png)。
2. [实际裁片与粉色绘制域](qa/F062_crop_and_edit_domain_PENDING.png)，对应 [470×780透明输入](reference/F062_crop_RGBA_NOT_ART.png) 和 [白改黑保掩模](masks/F062_crop_WHITE_EDIT_PENDING.png)。
3. [近鞋原位与远鞋过步](qa/actual_fixed_near_and_swing_far_feet.png)。

采用19:47已批的近链：髋 `(886.855797,603.286522)`、膝 `(893.275644,772.873817)`、实体踝 `(833.856190,957.811814)`，均为原生坐标。源藏髋 `(805,595)` 只是施工代理；本态髋比057下3.017152world，相对头衣原节拍下6.193040world。投影段长保留61.791576／70.726820world，鞋踝不拉、不滚、不滑；实际近鞋底仍为774.874331world。

白区从腰臀连接到整近裤腿、膝后转面和裤口，包含旧碎片裂口及旧／新边清理区，不沿旧拼缝锁死。两条裤腿均待真实绘图，棕色远髋是明确标示的手工形体层次提示。头衣保持原节拍；真实可见整臂、手、玉镯和鞋踝保护，仅放开小袖根连接。保护按实际可见前后层次计算，隐藏远鞋不能锁住前景裤体。

唯一人物源为已锁 e3d2202 的 [F057原RGBA](../../F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png)，SHA `93939f3e148c0a957ef418c677e60cc3fd27cf6b6844f91d500c8a3508b76720`。髋鞋入口沿77ab772，必要旧提取掩模与几何原文快照位于 `sources/`；快照中的旧绝对髋定义不作为本次新近链。重放入口为 [prepare.py](prepare.py)，根独立核验为 [root_input_audit.py](root_input_audit.py)；结果见 [root_actual_input_review.json](root_actual_input_review.json) 与 [preparation_checks.json](geometry/preparation_checks.json)。

独立核验：近鞋RGBA变化0，头衣整层严格符合原节拍平移；103519px白区与三类保护域交叠0，新近髋／膝／裤口同一白区连通。另在独立临时目录仅保留本包与两项已提交源，删去全部生成目录后重跑，32张PNG的SHA全部一致，见 [独立重放结果](isolated_replay_checks.json)。

本包仅交输入和保护域，不登记整镜ready，不改共享实现或文档，不启动渲染。
