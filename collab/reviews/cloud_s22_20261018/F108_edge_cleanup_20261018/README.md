# S22 F108指定外缘清理：零生成小交付

唯一最终RGBA：[F108_edge_fixed.png](candidate/F108_edge_fixed.png)。完整SHA256：`e0d31242883ad1dca5e5ce1c838257228e5d980ace1605ea93e2a31349f5a704`。

按Astra最新实审只清源图闭区间x158–167/y913–940。实际148像素改变，区域外RGBA逐字节一致；接触群未变，真实斜黑轮廓核心未变。x166/y914–916竖尖从同图紧邻完整列x167取真实像素接回；下拖边只清裁切末行延伸，用同图边缘alpha接续，没有重新画手、加色或生图。原始输出、旧108及已锁114和其他11态均保持原字节。

已实际打开：[灰底15倍前后](qa/before_after_gray_15x.png)、[深底15倍前后](qa/before_after_dark_15x.png)、[全幅灰底](qa/F108_after_on_gray.png)。竖尖和拖边消失，斜黑轮廓与相邻肤色连续。准确改动遮罩见[masks/actual_changed.png](masks/actual_changed.png)，来源/逐点断言见[cleanup_checks.json](provenance/cleanup_checks.json)，可复现脚本[cleanup_same_pixels.py](cleanup_same_pixels.py)。

旧108来源：`fourth_push_108_114/F108/candidate/F108_final_edge_aligned.png`，SHA `d80948993838a76c0ea788e7111e9c245b9457c34dea2fb9da49ddc1080b74f0`。114保持`74b692c116bf4d72e7d0fb684910b852e4c91ed32cfbe84d704e22a44f217112`。新图像调用0，原raw及原提示词仍在原包。

本小包先提交供Astra查阅；后续完整120帧实景须绑定本页唯一新SHA。[Astra修后直接接景授权](provenance/authorization.json)已收到，保持12原态曝光，不改共享EDL/音轨/ready或生产分支。
