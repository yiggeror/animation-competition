# S09 当前完整试件与044/063同尺灯体握持固定小包

按 Astra 最新要求固定后停止微调。本包零新图像调用，069未开启；没有改变68cde1d9的试合成、共同M、手臂或补衣。完整试件仍为 **HOLD**，不是通过稿。

先看 [灰底同尺完整灯/握手与轮廓](comparison/gray_actual_same_TL_complete_prop_grip_and_contours_1x.png)、[深底同尺对照](comparison/dark_actual_same_TL_complete_prop_grip_and_contours_1x.png)，再看 [063原始完整握筒上下文1:1](comparison/F063_RAW_full_torch_and_grasp_context_1x.png)、[044原完整灯与握手1:1](comparison/F044_original_whole_unit_and_grasp_1x.png)、[044实际母图整灯近手上下文1:1](comparison/F044_flat_mother_whole_torch_and_near_hand_context_1x.png)。这些真实图均已实际打开查看。

[当前完整试合成灰底](fixed_trial/full_registered_026_trial_gray.png)／[深底](fixed_trial/full_registered_026_trial_dark.png)；[完整连接处深底2倍查看](qa/current_fixed_complete_trial_connections_dark_2x.png)。原透明试件SHA保持 `6ca8123da6afd1eafe7c78b51e819aac352bc9d90d3de0c6a988d3fdecf606e9`；完整原始063 RAW与044全母图另在 sources，不只提供局部。

## 比较约束与结论

- 044整灯与原握手作为一个完整组，原比例s1、R+78.508°，仅为审查对照投到早已冻结的T/L。未加入当前063试件；没有把腕端历史技术边冒称合格新臂。
- 063直接复制68cde已存的完整新臂／握手／整灯共同M输出（s0.542209296288587、R−2.379877°），本包没有另缩手、臂或灯。两者共同轴长376.001330native；对照裁切(800,480,1290,720)，每个实际对照面板均1native像素=1图像素。
- 同轴长后，063完整尾端投影主径55.72±3.25native，对044约83±4，约少33%。独立材料横截量80.07对55.37也保留供参考。都是2D可见投影与手工取点，不冒称3D实体量具结果。共同相似变换不能修正径长比。
- 青/橙为两完整可见组alpha128外轮廓，包含握手与裁切内手臂；没有补画手后隐藏的筒轮廓。对照仅呈现真实可见材质。
- 原044独立b877整组与fe70压平母图的历史来源差异已在前包说明：alpha128内104处RGBA不同（alpha255内17处）；因此本包同时附两来源实图，不声称两个来源逐RGBA相同。
- 当前试件仍有袖口／衣缘缝隙、原衣线残片和253个alpha128新近臂与稳定裙区重叠；本包不会继续用碎衣或变换追到通过。原头／领／近袖褶／稳定裙保护继续保持原已验证RGBA0变化。

由 Astra 看实际完整新握筒与旧044原组后，决定保留原完整道具握手组仅接新臂，或最小一次完整握持形体修。本包没有执行任何方向，也没有新069输入或生成。

## 来源、提示词与复核

18项快照在 [来源清单](sources/snapshot_manifest.json)，共同M与旧整组刚性矩阵在 [几何及限制](qa/fixed_comparison_geometry_and_limits.json)。全提示词、精确参数、完整原始工具返回与原输出仍保留于 [原局部修调用包](../F063_local_repair_call01_e6619045/README.md)：[完整提示词](../F063_local_repair_call01_e6619045/requests/prompt_call01_EXACT.txt)、[精确参数](../F063_local_repair_call01_e6619045/requests/arguments_call01_EXACT.json)、[完整原始返回](../F063_local_repair_call01_e6619045/requests/call01_raw_tool_return.json)。没有重新请求或改写原始输出。

`python verify_fixed_bundle.py`只读复核所有快照的git字节、试件SHA、完整新组不变、044整组s1变换重放、同尺面板与原图裁切。完整试件原构建/验真脚本仍在相邻 `F063_same_source_registration_gate_20261019/`，本包不改它们。
