# F128 唯一原件接收，待实际最小门

- [唯一原件](raw_original.png)
- [完整正常灰底](actual_full_gray_1x.jpg)
- [正常双掌和真实有限杆](CAM20_F128_true_finite_rods_both_palms_albedo_1x.png)；[3×两夹口](CAM20_F128_true_finite_two_grips_albedo_3x.png)
- [原 CAM20 单张实际接景](CAM20_F128_current_branch_actual.png)；[同机位 albedo](CAM20_F128_current_branch_albedo.png)
- [120 左 / 128 右同尺](120_left_actual128_right_same_canvas_upper_hands_1x.png)
- [完整裙根腿鞋支持对照](120_left_actual128_right_whole_roots_legs_support_1x.png)；[裙根正常倍率](actual_under_hem_1x.png)
- [候选 PNG](F128_uniform_registered_whole_native_upper_fixed_full_lower_CANDIDATE.png)；[候选 SHA](FINAL_PNG_SHA256.txt)

本轮按 Astra 对 `0feec699` 的实际输入门授权执行 **1 请求、1 原件、0 重试**，未开放 132、未冻结曝光。四输入实际快照、实际 prompt/参数、完整原始工具返回及真实请求 mask 均保留。`tool_return_original.json` 中的 PNG 字节与保存原件 SHA 完全一致。

原件构图漂移，只对完整新头颈胸、双臂掌、整裙及短导向段作一次统一相似注册：s=0.7424531408883115，顺时针 0.3471930438129408°，t=(45.40469145686643,173.33674154616097)。两处实测原生夹口映射至已定 B。没有独挪头掌、剪指、修臂或按白域轮廓硬切裙臂；整条新原生裙摆以实际衣料/裸腿边界分离，原生外伸裙褶完整保留。生成腿鞋未采用，接原完整固定腿根支持。

**保留待门审的偏差：**R 原生短导向段相对真 T_H 约 -12.007°，接景可见额外短分叉；L 短导向约 +0.996°，掌下有一小段原生绘制尾。没有擦掉它们，也没有移动/缩短真杆、修改原偶根位来掩盖。终端圆帽在 master 栅格中被完整原生组件覆盖的采样为 R 12/12、L 10/13，不能据此声称两掌接触已终审通过。头颈姿态、头部落点和裙形也与施工参考不同，均保留实际形体交门。

原 CAM20 只实际渲染 F128 一张。原 turtle scale=1.3、facing、120→128 原 pose/roll、已定根位、两根有限 A→B 的世界/屏幕端点与长度、相机/人物注册均逐项等于本轮已过的机构输入基准。没有生成龟偶或长杆。完整固定腿鞋、奶奶、可见 C 与已定源逐像素保护为 0 变化。

重查：`python audit_actual_and_crops.py`。该命令只读既有单帧并写局部裁图/审计，不调用图像工具、不重绘场景。详见 `ACTUAL_SCENE_AND_RECEIVING_AUDIT.json` 和 `registration_and_protection.json`。当前候选未采用，等待 Astra 给最小门。
