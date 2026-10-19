# F022 整臂统一接回候选｜零生图，实际AA余量未过

已按Astra给定矩阵保留完整真掌、镯、腕肘和袖口接回，**F022仍未锁，026/030不绑定**。唯一未过的实际接触门：拇指可见边已贴上签、可见重叠0；余指／掌包含全部外AA的最小空气为 **√5 = 2.2361场景像素**，小于要求3。最近点为人物 `(970,773)` 的 **alpha1** 像素，对真实上签 `(972,776)`；没有丢弃这点冒称通过。下签余量16像素。

- [完整native候选](candidate/F022.png)，SHA `2c28bafe7ee05c5b234711fc551dd2a4d358143ea2615dc0a2282428aa744332`。
- [真实Canvas全景](actual_scene/F022_canvas.png)，SHA `1a0732e0fc879d086c04255dfdb507799d2be59fd21bfc91be025fd9cf809a2f`；[实际首触无损10倍](actual_scene/F022_actual_contact10x.png)、[实际肩接回4倍](actual_scene/F022_actual_shoulder4x.png)、[native肩接回3倍](qa/03_shoulder_join3x.png) 均已实看。
- [旧远臂实际所有权](masks/old_far_arm_actual_ownership.png)、[新臂实际所有权](masks/new_far_arm_actual_ownership.png)、[可见新臂独占域](masks/new_arm_visible_exclusive_ownership.png)。沿真实前景领襟折线分所有权，没有用宽GUIDE清空全身。[远臂层](candidate/F022_far_arm_exclusive.png) 与 [静态层](candidate/F022_static_exclusive.png) 互斥、逐RGBA重建完整候选；没有代码手指。

[精确矩阵](provenance/uniform_matrix.json) 与输入一致：`[[.435717950246291,.061236164422429,523.198762766005],[-.061236164422429,.435717950246291,572.695273541552]]`。最终额外整臂平移为 `(0,0)`。仅肩帽布片使用同源纹理的平滑局部位移 `(+15,-36)`，最大39native；到y755衰减归零，袖口以下皮肤、腕掌及全部手指仍为同一统一映射。没有复制花朵补缝。新臂蓝布／肤／玉镯按原022固定语义明暗域对齐；花瓣、墨线、折影和alpha保留，原身体不重新修色。

原臂 `6e87f65ad06119f6483ba02bbfa072117f7fc1dcc32e4c79b374b67e7e41d543` 和静态022 `938682ddf40b13e6b72dbacbabedf9502ae73bba79944b330aae6a3bedb26234` 未动。旧／新所有权域外RGBA（含alpha0隐藏RGB）、近右臂与头颈保护域、6个原膝胫脚背接地区的RGBA均与原022相同。真实道具层PNG与冻结018字节全同，箱／鹤布托／光相机函数沿用原入口。

[有限微调检查](qa/actual_Chrome_micro_probe.json)：在≤1native范围先按0.1网格做软件预筛，再测25个整片候选的真实Chrome alpha注册；没有同时满足可见首触与其余外AA≥3的候选。零平移的探针与真实全景alpha逐点完全相同；未选中任何微调，也不声称离散采样证明连续空间无解。所有试验只重采样真实原件alpha，没有移动单指、擦墨或挪杆。

[最终检查](qa/FINAL_REVIEW.json)、[真实资源日志](qa/actual_canvas_network_events.jsonl)、材色统计及复现脚本齐全。实际F022渲两次，PNG逐字节相同；第二次只为核验恢复域外alpha0隐藏RGB后的最终源SHA，所有可见native像素和alpha均未变。新生图0，累计仍7。早期原生肩根切分诊断保留在 `qa/preflight*`，不作成品；当前只交候选与AA阻碍，待Astra决定下一步。
