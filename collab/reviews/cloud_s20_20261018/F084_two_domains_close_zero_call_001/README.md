# F084 两域零调用收口候选（待 Astra 终审）

本包新增图像调用 **0**，只处理 `07690a02a51bba4652cc06d1ef7f6fc73ab8eb1e` 的本份084。原始生图、完整请求、四输入与原件来源仍在 `../next_F084_peak_input_001/generation_001/`，未覆盖。未采用、未扩态、未冻曝光。

- **先看实图**：[正常全图](actual_full_gray_1x.jpg)、[透明完整PNG](F084_two_domains_closed_candidate.png)、[两真杆/双掌正常](actual_two_true_rods_contacts_1x.png)、[3倍接触](actual_two_true_rods_contacts_3x.png)。
- **同尺对照**：[079左／修后084右完整头颈](079_left_repaired084_right_head_neck_same_canvas_1x.png)、[079左／修后084右肩肘与动作](079_left_repaired084_right_upper_hands_action_same_canvas_1x.png)。两侧是相同画布坐标裁片，未分别对齐或缩放。
- **第三杆**：保留原T_H、T_S及X/夹点像素；删除远上掌至近下掌间陡斜连接杆。空气区恢复透明，遮住的掌内肤面沿本份084邻接皮肤延续，接回中断的掌/拇指轮廓。保留本份真实卷指和完整腕；不贴079掌、不缩短真杆、不移夹点。显式完整掌域、删杆、肤面和真杆保护mask齐备。
- **头颈**：本份完整头发、脸、马尾、红花统一缩量 **0.9271687753**，无新增转角、不分移五官；颈部同一逆映射在原斜领口上25px内连续衰减至固定根。主发块同尺宽：正确079 **208px**，原084 **225px**，修后084 **209px**；主发块面积较正确079约+2.7%。079仅供测量，未借像素。
- **保护**：两真杆含夹点、肩臂/躯干整裙、固定白领、下肢鞋、奶奶及两域外RGBA变化均 **0**。原C层/轴不动，仅重新显露被缩小头发释放的部分。[颈领3倍](actual_neck_collar_3x.png)、[裙根3倍](actual_under_hem_3x.png)、[脚部2倍](actual_support_2x.png)。

最短来源/保护记录见 `repair_and_protection.json`，处理脚本 `repair_once.py`。全图、正常/3倍接触、同尺头颈/动作、颈领/裙根/脚部均已实看；指掌腕与头颈躯干鞋连通检查通过。最终PNG SHA256见 `FINAL_PNG_SHA256.txt`。
