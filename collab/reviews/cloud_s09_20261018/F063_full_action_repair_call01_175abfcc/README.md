# S09 F063 完整动作形体修唯一call01：实际审HOLD

**一次请求、一张原件，无重试；没有生产候选、没有069。** 原件已先以1d8e86e9推送，本包补固定逆配准和真实材质实审。 [完整原件](originals/F063_full_action_call01_RAW.png)，SHA `be78fe901b39d838c867326b517ed26ee72ed6488c683f94e06b0487a6df020f`；[灰底实图](qa/actual_RAW_full_gray.png)／[完整动作近图](qa/actual_RAW_full_action_dark_1p5x.png)。

## 当前阻断

[冻结target对固定逆贴灰底](qa/frozen_target_vs_LITERAL_inverse_gray_HOLD.png)／[深底](qa/frozen_target_vs_LITERAL_inverse_dark_HOLD.png)。输出实际1145×1374，冻结输入1280×1536；严格只用77/128+[550,0]后，角色与道具整体偏小且T/L不合。没有静默改逆配准或对局部拟合。原头领／近ruffle／稳定裙尚未恢复，因为此图注册未成立。

[实际源坐标和真实材料量法](geometry/fixed_inverse_actual_shape_and_gap_HOLD.json)：手工端面中心T=(438,922)、L=(1007,832)，各±7raw。固定逆配准轴长约346.54native，对冻结376.00；尾帽可见材料跨度约57.88，对原80–83；红筒约68.82，对68；灯帽约119.84，对124。尾帽中性／墨线ROI是保守可见包络，边邻白点／手边可能混入数raw，不能冒称3D实体量具。即便这个偏宽量法，尾帽／全轴比例仍较原044约少21.56%，与统一缩放无关；不能靠更换画布缩放修正径长比。

[实际掌到灯缘灰底3倍](qa/actual_far_palm_to_prop_contour_gap_gray_3x.png)：真实材质轮廓α128=13.928raw→8.379native；α16≈7.219native，α1≈5.546native，仍有空气但未达到输入约15。近握位置向尾部移，滑键未明确露出；远侧大而低的袖口、自己的远上臂在近前臂后的连续起源、近腕／近ruffle与裙边需Astra实际结构审，不能以像素相连宣称通过。[root实际审](qa/root_actual_fixed_inverse_HOLD_review.json)。

包内diagnostic透明整图仅为**指定逆配准诊断**，不作为候选。未做图像级画布归一化；数据表另列假设统一归一化的数字供审查，明确未授权采用。没有非等比拉筒、碎衣填洞或独立移动手／臂／灯。

## 完整来源与唯一请求

175abfcc全部78项冻结输入在frozen_input_175abfcc，五图逐字节不变。[最终完整提示词](requests/prompt_call01_FINAL_EXACT.txt)只在原388词后逐字追加指定远上臂句，文件SHA `ac700bb6a3b0d46ce8564e7c14804078e8670a2b97e15038581d14339ed751b0`；实际prompt字符串SHA `71d128b5fa8dd386f6b15c655aa08678d49537df508e31bcab89ca72e05c35f7`。[最终精确request](requests/arguments_call01_FINAL_EXACT.json)，SHA `1bf32a103707026023b0a0515509ce2a2751f678ede5db7ce3569bd723f140b4`。

[完整原始返回](requests/call01_raw_tool_return.json)含全部base64；宿主 `/workspace/generated_images/exec-24764e12-b81f-4b27-a056-0c383e98230f.png`原地保留，宿主／归档／返回解码PNG三方逐字节同。权限原文、最终SHA和一次计数均在requests。`python verify_actual_archive.py`只读核全部冻结git字节、五图、精确追加句、SHA、唯一计数、三方原件及唯一固定逆配准。`audit_fixed_inverse.py`可重放诊断，绝不调用图像工具。

此包停在真实审HOLD，交Astra决定后续方向；不自行重试或开启069。S07 F100仍只准备输入。
