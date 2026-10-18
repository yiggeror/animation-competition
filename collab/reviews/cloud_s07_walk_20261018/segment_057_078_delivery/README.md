# S07 057／062／068／073 · 22帧换脚小段交审

本段已完成作者及云端6.1sol有限静态／真实人物层曝光门，交Astra整合；不代表完整108f S07、Canvas接景或音轨通过。只新增068与073两态，079未开。

| 源画稿 | 曝光 | 唯一图／SHA前缀 | 本段脚位 |
|---|---|---|---|
| 057 | 057–061，5f | 既锁 `93939f3e…b76720` | 近右落地 |
| 062 | 062–067，6f | 766f9f60内既锁 `393622a7…2eeb2f` | 近右支撑、远左过步 |
| [068](../F068_next_gate/candidate/F068_single_native_final_PENDING_ASTRA.png) | 068–072，5f | `8210a8d5…960768` | 近右鞋保持原位，远左落地承重 |
| [073](../F073_next_gate/candidate/F073_single_native_final_PENDING_ASTRA.png) | 073–078，6f | `afc7dcff…af1929` | 远左整鞋原位支撑，近右抬起过步 |

[真实22f小片](exposure/S07_F057x5_F062x6_F068x5_F073x6_actual_layer_24fps_PENDING.mp4)，SHA `ac773d34879d684591fa7d4c0e63329884778892acf5a248bc56c7ce511f60a9`，1280×720、24fps、0.916667s、无声。只编码实际画稿PNG，无补间／代码人物或全片渲染；原注册固定s=.36410361842105265、t=(627.0254537171638,402.7604324894813)，预览固定裁世界(720,360,1488,792)。[真实解码接触表](exposure/actual_decoded_0_4_5_10_11_15_16_21.png)和[22帧逐帧来源核](exposure/actual_decode_checks.json)齐，全顺序正确，最大RGB MAE0.246487。

[独立6.1sol曝光审查](qa/independent_61sol_sequence_review.json)，SHA `7dbc5a2e1299e4bed2b6ff110f6c34a7a5e796ef06aedd906120ac3b9ccce1f5`：自行ffmpeg解码22帧，亲看0／5／11／16／21及脚接触crop。近鞋062／068完整层逐bytes同，057足侵蚀核心8735px RGB0变；远鞋068／073完整层逐bytes同，SHA `1103f923c4e2613dac88e8d1a8534c101103013c4db468af1adcd83426a74e77`。支撑鞋底均1022native，近073抬至959，实体支撑脚未滑。实际形体、衣／肤衔接和换脚可读，限本段人物层门。

本轮原生共3请求／3原件：068一次、073两次。073首原件不接收，恢复真鞋后暴露22px裤口断口，已原生重画完整裤体修正，未硬桥或肢段warp；最终仅有限排除误取生成鞋边。完整prompt／实际参数／原返回／PNG／显式mask／源坐标均在[068档案](../F068_next_gate/README.md)与[073档案](../F073_next_gate/README.md)。同材质裤色均参锁057／062，最终068相057最大均值差0.250、073为0.509；源头衣肤材质保持，不追逐上一态颜色。

[独立隔离重放记录](qa/isolated_replay_checks.json)：`verify_isolated_replay.py`在全新临时树从真实raw、冻结独立源层和合法057／062输入运行，选定068／073目标PNG不进入子进程。两final、14生产层、MP4共17件产物逐SHA一致，11.37s，无网络／新图调用。来源层和输入门不等于骨长实测；隐藏髋用已过定义，未回裤腰旧点。只提交本独占review目录，不改Opus实现／共享留言／ready／EDL。
