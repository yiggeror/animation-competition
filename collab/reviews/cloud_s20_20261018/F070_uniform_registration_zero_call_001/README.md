> Astra终门已通过并采用本PNG（e10e2b65；SHA1d12ca87…）。不重修、不重复生成。以下保留交审时历史说明，采用记录见ADOPTED_F070_SOURCE.json。

# F070完整组件统一注册：零调用候选

先看 `actual_full_gray_1x.jpg`：已将750baee4那份原件的新头颈、躯干、完整双臂掌腕、整条新裙及两根T杆作为一个连续组件统一注册，原件本身保全。0次新图像调用，原生组件到最终画布仅一次重采样；未分别变换手臂、手掌、杆或裙。

主发块、胸腰体量及两侧裙根的实际对应点联合拟合：**等比0.833505287，整体顺时针2.454634°，原点平移(+18.529705,+115.044899)px**。矩阵、对应点和6.743px联合残差见 `registration_and_protection.json`。没有沿用视觉估值作为强制参数。

整裙自然覆盖已锁067完整腿根；只清除裙下新露出的少量旧裙边残线，使用同一固定远腿肤色，清理mask和贴层随包。固定腿层原文件不变，腿形与alpha不变；未挪膝踝或双鞋。除这段旧衣残边清理外，未遮挡的固定下肢RGBA变化0，双足支持前景与奶奶人体前景RGBA变化0。

已实际查看以下图：

- `actual_full_gray_1x.jpg`：完整正常尺寸灰图。
- `067_left_registered070_right_upper_1x.png`、`067_left_registered070_right_skirt_roots_1x.png`：067左／注册070右，同尺上身与裙根。
- `actual_contacts_1x.png`、`actual_contacts_3x.png`：双掌/X，一起注册后仍可读，R→T_H、L→T_S，T_S在前。
- `actual_under_hem_1x.png`、`actual_under_hem_3x.png`：自然整裙与保留腿根的遮挡。
- `actual_support_1x.png`、`actual_support_2x.png`：锁定双足支持。

最终透明PNG：`F070_uniform_registered_upper_fixed_full_lower_candidate.png`。PNG SHA、原件/完整原生组件/固定腿层来源SHA、变换与像素校验见JSON及SHA256SUMS。仅交Astra终门，未采用、未传播、未扩后态、未冻结曝光。
