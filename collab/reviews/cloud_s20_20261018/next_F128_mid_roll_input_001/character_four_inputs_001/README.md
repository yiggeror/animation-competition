# F128 四输入，0 调用，待实际输入门

- [完整唯一目标](inputs/01_unique_complete_F128_target_REVIEW_ONLY.png)
- [正常倍率双掌与有限杆接触](contacts_1x_REVIEW_ONLY.png)；实际输入为同图 3×。
- [真实完整 mask](inputs/04_complete_upper_whole_skirt_white_full_legs_black_mask.png)
- [F120 身份局部](inputs/03_120_identity_head_collar_cloth_shoes_patches_only.png)
- [四输入 SHA](FOUR_INPUT_SHA256SUMS)

这是一张连续整上身施工参考，不是新原生绘图。头整体保持体量，小幅后收并抬起注意方向；颈胸肩跟随，双肘按相同投影骨长接回，腰裙向固定腿根衰减。袖下、胸腰与隐蔽腿根均交给完整白域自然重绘。

两个握点保持本轮实际机构门通过的完整精度；人物目标只含各自有限轴上的接触短段，止于自己的 B。原龟、完整 A–B 长杆及其翻转姿态留在外部接景参照，四输入不含需要重新生成的龟偶。没有第三杆，也不要求翻转中强制保留旧 X。

本轮才确立的输入基准另存于 `MECHANISM_INPUT_BASELINE_THIS_GATE.json`，历史候选文件保持原样。来源为机构门提交 `a4f70c3a4d0e11d57d17cb32783ed7763dcb6cae`，原始 F120 文件不改。

`prepare_only.py` 仅做参考施工；`verify_only.py` 检查四图 SHA、完整腿鞋/奶奶/可见 C 的原像素、真黑白 mask、握点与投影骨长。完整掌形插值最大残差已压至 R 0.038 / L 0.020 px；握点控制残差小于 1e-6 px。详见 `VERIFICATION.json`。

提示词与四图顺序已准备，文件名带 `NOT_SUBMITTED`。本轮 0 请求、0 原始输出、0 重试；未冻结曝光、未开放后续态。等待 Astra 对实际四输入短门审查后再单独授权原生生成。
