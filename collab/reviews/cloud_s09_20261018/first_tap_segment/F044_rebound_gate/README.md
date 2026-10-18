# S09 第一击回弹044与恢复048 · 交 Astra 实图审

044 唯一取图：[F044_complete_local_native_arm_PENDING_ASTRA.png](candidate/F044_complete_local_native_arm_PENDING_ASTRA.png)，SHA `fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9`，1672×941 RGBA。作者已实际查看灰／深底和真实解码；不自代 Astra 锁图。

既有6.1sol现已独立实看灰／深底、4×腕口及自行ffmpeg解码10f，有限PASS袖根／腕口／远袖层次及本段因果；腕缘约1～2native像素墨阶未列为结构阻断。[独审JSON](qa/independent_61sol_output_review.json)，SHA `e9a0715f011006e4f38e715582b661e887ab208580f97b439b92ffee07b4354f`。048容差仍由Astra裁定。作者重放五脚本的四份关键PNG／MP4逐SHA同，见[作者实图与重放记录](qa/author_actual_and_replay_review.json)。

原锁042为 `52bb96f9796878bbb9c928ad80c5af6b5a0580ad9f9c651384446f0caadd3f8f`。044整件真实原握手＋手电上移48native，缩放1、旋转0、无重采样，尾盖离固定掌48行＝30.2267registered px；原031轴端(1135,278)→(1134,654)，长度376native≈236.8registered，沿已锁约240px口径，不用旧撤回的直径数。固定掌取037纯掌源，接触复合AA仅从同一031道具层／037纯掌恢复，未把掌皮随筒带走。真实原近ruffle及掌按实际材质mask一次恢复，无透明矩形护栏。

044新增原生2请求／2原件：call01完整近臂，call02局部根／腕／臂下露空接续。call01整臂仅作一次−2.8°刚体对位，scale1，无分段拉伸；原生call02重新形成同框内完整可见近臂。最终使用call02实际整块近臂材质、真实轮廓和臂下衣料，不机械沿小白域切碎新轮廓；实际采用范围为[complete_local_native_arm_adoption.png](connection_call02/masks/complete_local_native_arm_adoption.png)。原生图中移动的腰带、头、握掌／手电不接收。

原严格小mask回贴出现锯齿／色缝，`F044_native_connections_PENDING_ACTUAL_REVIEW.png`及其他`TRIAL`、`native_exact_domain`均是历史未通过试取，**不得取用**。最终完整材质取层范围41943px，含实际新近臂33039px。腕源技术提取边释放90px；其余真实手筒的物理几何不动。手筒源alpha255核心640px逐RGBA相同，alpha≥240材质中13个近端AA像素因真实臂底层合成出现+1～2alpha，其中1像素RGB各+1；不能说所有AA字节相同。整个尾筒y>590含AA6054px逐RGBA0差。固定掌、原近ruffle实际mask逐RGBA0差，未用平面alpha锁打洞。

新近臂分阴影／平涂／高光三簇与母042比较，最大通道均值差3.369，未校色。见[semantic_skin_color_checks.json](qa/semantic_skin_color_checks.json)。这是同材质颜色检查；隐藏关节不能从2D轮廓精确量出骨长，不能把投影中心线当真实骨长冻结。实际比例、前后遮挡和袖根／腕口仍以实图审为准。

048×4暂以[真实已锁037整图复用](../F048_recovery_reuse_gate/candidate/F048_recovery_TRUE_LOCKED_F037_REUSE_PENDING_ASTRA.png)交审，SHA `68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9`；**不是新生成原件，也未用代码造臂**。这是恢复到同一首蓄势高位的完整真实pose，掌／头眼／握筒均同源。其间隙实测91native＝57.3048registered，比名义55多2.3048px，请Astra明确容差；若不接受，再从本次冻结源绘048，不冒称已精确55。见[048复用及实际间隙](../F048_recovery_reuse_gate/qa/reuse_and_gap_checks.json)。052／056仍暂停。

[真实曝光小片](exposure/S09_F042x2_F044x4_F048x4_actual_layer_24fps_PENDING.mp4)：042×2→044×4→048×4，10f／24fps、1280×720、无补间／无音轨，只有实际PNG层，不是全镜或全片渲染。[实际解码接触表](exposure/actual_decoded_0_1_2_5_6_9.png)已看0/1/2/5/6/9；[逐帧来源核](exposure/actual_decode_checks.json)全部10f顺序正确，最大RGB MAE0.783。不替代实际背景合成、全96f双击因果或声画通过。

完整两次提示词、实际参数、输入冻结和工具原返回分别在[requests/](requests/)与[connection_call02/requests/](connection_call02/requests/)。两原件保存在[call01原图](originals/F044_call01_raw.png)（SHA3d0561f4…fc25a4）和[call02原图](connection_call02/originals/F044_call02_raw.png)（SHA4c29d29c…9e2b2b）。工具返回base64、host原图和归档PNG已逐字节核同；源快照见[sources/snapshot_manifest.json](sources/snapshot_manifest.json)。原始PREPARED及失败试取保留历史，不改已执行输入。

本包S09累计19实际请求／18实际原件；048新增调用0，未重送历史被拦请求，未调用新付费服务／API。重放顺序：`assemble_native.py`→`compose_semantic_arm_trial.py`→`connection_call02/adopt.py`→`connection_call02/adopt_complete_local_arm.py`→`finalize_and_expose.py`。前两个`prepare*.py`为已执行输入记录，不在请求后重跑。
