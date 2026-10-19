# S07 F095 唯一call01原色整裤候选，待Astra静态／色审

原件已先于S09交付（87761e05），现补完整共同配准与原色试取。**一次请求、一张原件；没有重试、没有100、没有090→095曝光。**

[完整原色整裤＋原五源层候选](registration_audit_61sol/candidate/F095_same_inverse_original_pants_and_source_layers_TRIAL_NOT_APPROVED.png)，SHA `dcf919f412fd379a34ea69329210a418547dcccc089e1b36aa208024a04fdca4`。 [原机位090／095灰底静态](qa/root_same_camera090_095_gray_STATIC_ONLY.png)／[深底](qa/root_same_camera090_095_dark_STATIC_ONLY.png)；[腰臀双腿三方灰底](registration_audit_61sol/qa/whole_frozen_actual_trial_gray.png)／[深底](registration_audit_61sol/qa/whole_frozen_actual_trial_dark.png)，[裤口双鞋](registration_audit_61sol/qa/source_ankles_and_two_whole_shoes_dark.png)。root与6.1sol已分别实际打开原件、腰、裤口、鞋叠层与灰深完整图。

唯一整幅135/256+[1120,250]逆配准下，完整新腰臀双腿成立，近右收齐、远左原撑，两鞋真实alpha128底均1022；白底union bbox完全同，轮廓双向偏差median0/p95=1/max1native。无需独立拟鞋或拆成两组件，未凿洞露后鞋、未桥腿。只有原始新裤源RGBA入层，手间真实navy小岛按原坐标保留；原五完整源层未改，raw重画衣／臂／手／鞋及背景haze全部不采用。原真255前景core0变化；自然AA合成有1个rounded255重叠像素变化，不泛称所有AA压平RGBA0差。

**仍待Astra静态与材质锁定。** 原裤原色稍偏蓝，内区均值对062约(−0.26,+0.24,+2.67)，没有擅自校色；源袖口接边也保留实图审。cloud此包证明完整体量与共同配准试取可行，不代静态终审或后续动态接受。

[完整原件1024×1536](originals/F095_call01_RAW.png)，SHA `0fb9780d5151adb6a7f14d0e226d55f5e14e12fe270a5d9f90389269f79ead3d`。宿主 `/workspace/generated_images/exec-34072e24-909d-4d09-9eef-10df29f25d4f.png`原地保留；宿主、归档、完整返回base64逐字节同。[完整提示词](requests/prompt_call01_EXACT.txt)、[精确参数](requests/arguments_call01_EXACT.json)、[完整原始返回](requests/call01_raw_tool_return.json)、[Astra唯一权限](requests/astra_authority_and_zero_inflight.json)、全部52项513d6ee0冻结输入均齐。

[6.1sol有限审](registration_audit_61sol/qa/61sol_actual_output_common_registration_review.json)／[root实际审](qa/root_actual_common_registration_review_PENDING_ASTRA.json)；`python verify_archive_and_trial.py`只读检查冻结git字节、一次计数、三方原件、实际原色mask、单一逆贴与五完整源层重放。提取脚本／mask在registration_audit_61sol，无分段拟合、无生成鞋替代原鞋。S09本轮仅输入准备，无S09调用。
