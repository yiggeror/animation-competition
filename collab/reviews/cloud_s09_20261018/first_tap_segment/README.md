# S09：已锁031后的037／042小序列

**最终本段：037仍未通过，042为0。** [最新真实重组](independent_recompose/F037_independent_original_pixels_PENDING.png)SHA526ca883…c48735已清旧悬片／U边／截白点，但远袖新露上缘缺实际连续黄料；[来源冲突证据](independent_recompose/far_sleeve_source_conflict.png)。503px全图微接缝call02未填谷口、不采用；[局部call03](cloth_connection_call03/README.md)输出阶段被工具moderation_blocked／other拦截，无新图，未重送。**S09累计15请求／14原件，037共3请求／2原件、采用0，无在途。** 完整[本段实际结论](qa/F037_actual_outcome.md)。042真实触掌门未做，不能拿技术预摆替代。

下面准备／诊断状态为阶段历史，完整输入及记录保留。

本包继承 Astra 明确通过的031整态，唯一源图固定于 `78a980dff69601083580a1df819789954f6d8947`，SHA `4b59c62485cf382c3e2d411de3c8ca9fb4edee622dad31b41946362889d44da7`。原生1672×941、原配准和机位不变。此前衣片及裙边修正已通过；不再沿用“031待审”的历史状态。

当前：**037已执行唯一call01，新调用1，S09本人累计13次；042为0，无在途请求。** 原件、完整返回均已保全；返回近臂／手筒额外上漂约30raw，未直接采用。整新近臂统一下移30raw可同时靠近原袖根与新腕根，正在同原件最小语义接回；诊断图均未采用，不作042续画源。技术预摆不是画稿。Astra 已授权031→037→042，依次实审，不提前批量派发。

- [完整尾盖／掌面实际三联图](qa/actual_tailcap_palm_triplet.png)：031实际锁母；037／042为完整原像素刚性预摆。037上32raw，042相对031下59raw（相对037下91raw）。手电与全握持手同移，无缩放、旋转或变形。
- [037预摆与局修范围](qa/F037_actual_preposition_and_domain.png)：新旧近臂轮廓、肘至腕、旧臂腾空衣片及旧手电空背景；袖根、头颈眼神、远臂掌、其余衣片及连续裙外缘冻结。
- [母源与目标记录](reference/approved_mother_and_targets.json)、[逐列完整盖缘／掌缘](reference/full_cap_palm_contour_rows.json)：实际完整轴376±8raw≈236.78注册px，沿此前约240规格的已接收真图，不强行再拉伸。完整尾盖约83±4raw，旧44raw可见片段撤回。
- [完整请求](requests/F037_call01_arguments.json)、[输入冻结](requests/F037_input_freeze.json)、[执行与原件记录](requests/F037_execution_state.json)、[完整原返回](requests/F037_call01_raw_return.json)。`originals/F037_call01_raw.png` 为原字节未改1671×941输出，SHA `d913073cf1fb4feaa9b0fcc89c68c4112b1acefe2279b4fd6ddc1022b8a61a9b`；base64解码与宿主PNG、归档PNG逐字节同。画布少一列，诊断只右补透明，不拉伸。

接触参考作了必要的实际轮廓细化：旧下移62raw／掌面722是近似施工值。逐列扫描整个尾盖与原掌面，在alpha>128轮廓下，下移59raw即可相邻，所有列均无实体交叠；62会略嵌入掌面。手电尺寸、掌位、接触动作设计均未改变。最终042仍须实看完整盖缘、掌厚、双前臂净空与真正接触，不把数值相邻当绘图通过。

`prepare.py` 只做已授权的原像素提取、刚性平移、透明合成和技术图。042预摆使用透明合成保留原掌尖，不能用整裁片矩形覆盖掌面。请求后禁止重跑准备覆盖冻结输入。`recompose_call01.py` 及当前candidate/QA中的DIAGNOSTIC均是接回诊断，腕／袖主连接已有改善，远袖旧边小残片、袖顶和衣点边界仍在独立复核，未判整态通过。所有派生遮罩与冻结输入分开保存，不冒称操作输入白域外零变化。
