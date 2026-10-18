# S07 068远左落地 · 单次原生候选

唯一交审图：[F068_single_native_final_PENDING_ASTRA.png](candidate/F068_single_native_final_PENDING_ASTRA.png)，1672×1080 RGBA，SHA `8210a8d56c15a42da4b4daa6c4a4599ce6b2df9b1f5fdab2e1403ec7f9960768`。068–072共5帧，远左落地、双支撑转远左承重。作者及[既有云端6.1sol独审](qa/independent_61sol_output_review.json)静态有限PASS，仍待Astra锁图及本段真实曝光门。

源母是766f9f60内062 `393622a77349083751122520b690bd35017f8535a25560d8cca775446d2eeb2f`。输入从真实生产层重组逐RGBA重现母图后再预摆，未退回旧裤或代理骨架。近右完整鞋原位，远左原完整鞋+181.2670807nativeX（66world）／+63nativeY落地；真实两足alpha128底均1022native＝774.8743305world。头衣相062增量(+42.2128629,+5.1774077)world；双臂各整块刚体小反相、scale1，真手／玉镯随所属完整臂，不分段变形。隐髋走已过062隐藏proxy定义，未回裤腰点、791／744等旧坐标，不把2D投影代理当解剖骨长。

原生仅一次请求／一份原件：[1024×1536原图](originals/F068_call01_raw.png)，SHA `8bd24bffbd4bc7328bd18fa383895a0c243dfd088883a11cea9edcc839a0b82e`。同框520×780输入，返回整块统一缩放0.5078125，贴回(700,280)，无额外旋转／位置修正／肢段拉伸。采用真实新裤双腿、连续腰臀、两膝与裤口，实际材质mask67154px；深色褶线把两腿navy分成两个大连通块，两块均完整取回。原始生成的头衣、手和新鞋不采用，只把完整原生裤层放在真实原衣、手臂和鞋层之间，远鞋在新裤后、近鞋在前，按真实AA合成，不用alpha0护栏切孔。

两处旧源归属已显式清理：输入前只从新派生body层移除164px旧远臂肤／墨及低alpha碎边，真蓝衣／白花alpha≥20删除0，冻结062与源快照未动，见[逐点源记录](geometry/derived_body_old_arm_cleanup_checks.json)。输出后旧far-foot提取层的裤缘悬支路在新裤外露，仅最终派生foot清46px旧ink／AA，真实裸踝及轮廓y936+逐RGBA0变；输入foot层不动，见[46点映射](qa/old_far_foot_trouser_branch_cleanup.json)与[清理前追源图](qa/F068_far_heel_actual_source_comparison.png)。其余真实整鞋和全身源材料保持；不是把旧裤残线解释为真鞋跟。

只对新navy作(−1,−2,−1)语义校色，原生alpha及maxRGB≤35深墨不动，保留原生褶影。锁色后均值对057母为(+0.250,+0.073,+0.094)，对062为(+0.003,+0.200,+0.468)，见[固定057色门](qa/color_gate_vs_fixed057.json)。头发、脸肤和蓝衫沿锁源材质，不随新态重新校色或逐态漂移。

实际看[灰底完整裤与接触](qa/F068_native_layered_crop_gray.png)、[深底全身](qa/F068_native_layered_full_dark.png)和[袖根／腰／脚口近图](qa/F068_native_connections_dark.png)。旧输入准备的`PREPARED_NOT_CALLED`文件仅作历史；当前[实际提示词](requests/prompt.txt)、[参数](requests/arguments.json)、[输入冻结](requests/input_freeze.json)、[完整原返回](requests/raw_return.json)、[调用账](requests/execution_state.json)齐。工具host原件、返回base64和归档PNG逐字节同。修后输入预摆SHA56d5e914…，完整白域108527px、SHA8fe70338…，输入独审SHAec24a30b…；失败诊断保留，不冒充当时已过。

重放只运行`compose_native.py`再把同SHA结果复制为唯一final；`prepare.py`是冻结的已执行输入准备，不能在请求后重跑。`candidate/F068_complete_native_layered_PENDING_ACTUAL_REVIEW.png`与唯一final当前逐字节相同，但交付索引只取上面的final。073从本068真实最终生产层继续；本文件的静态通过不代整个108f镜头或Canvas接景通过。
