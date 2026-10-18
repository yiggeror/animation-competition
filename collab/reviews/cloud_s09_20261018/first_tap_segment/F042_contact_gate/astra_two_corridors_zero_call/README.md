# S09 F042：两条残影走廊零调用增量，待 Astra 复核

基于已审动作、整臂、双袖与7帧的 `c909ea49…`，本轮仅清理 Astra 指定的两处残留。没有新增图像调用、整片渲染、调色、动作变更或额外缩放；044/048 仍未启动。

- [F042 透明候选](candidate/F042_two_corridors_clean_PENDING_ASTRA.png)，SHA256 `52bb96f9796878bbb9c928ad80c5af6b5a0580ad9f9c651384446f0caadd3f8f`。
- 两处实际修前/修后：[灰底](qa/two_corridors_before_after_gray.png)、[深底](qa/two_corridors_before_after_dark.png)。包含上腕整条轮廓，以及筒头、筒侧、筒尾到固定掌接触。
- [最终7帧曝光增量](exposure/S09_F037x5_F042x2_two_corridors_clean_24fps_PENDING.mp4)，SHA256 `966b02b01e4cc86ec207f169437ca5089ca6b338caa19af5f44f45313765d619`。037×5→042×2，24fps，1280×720，0.291667秒，无补间、无音频，仅实际PNG图层。
- [实际解码接触表](exposure/actual_decoded_0_4_5_6_contact_sheet.png)与[全部7帧解码检查](exposure/actual_decode_checks.json)：顺序正确，最大 RGB MAE 1.284591；已实际查看两色背景对照及解码帧。

上腕沿完整斜向轮廓及两端AA采用已存在的 call02 对齐原画像素：517像素进入采用掩模，386像素实际变化。手电外侧934个旧低透明残线像素采用原037整体下移91px的同位置透明像素；真实手筒材质及AA按实际源图保护，不以宽矩形包围残线。示例 `(1196,414)` 从 `[87,74,70,116]` 变为 `[0,0,0,0]`。

两条采用掩模外 RGBA 变化0；固定接收掌变化0；授权近腕走廊外真实握持及刚性手电变化0。检查与源图SHA见 [checks.json](checks.json)，可复现规则见 [clean_corridors.py](clean_corridors.py)。腕 donor 复用既有整块0.3125等比对齐结果，没有再次采样。手筒 donor 为完整037下移91px，与原031整件下移59px等价。

本轮新增调用0。S09累计仍为17请求/16原始输出；F042仍为2请求/2输出。原始提示词、参数、输入冻结与原始工具返回均保留于已提交的 [call01 requests](../requests/) 和 [call02 requests](../connection_call02/requests/)，本轮不复制或改写原始输出。

本包仅交付上述两区清理及7帧增量；不表示整镜或后续044/048通过。等待 Astra 合并复核。
