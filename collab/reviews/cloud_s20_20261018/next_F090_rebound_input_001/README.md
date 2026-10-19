# F090 峰后反向：单一零调用输入门

084独立态按Astra终门采用，未冻结持帧；来源见 `ADOPTED_F084_SOURCE.json`。本包仅**施工参考**，新增生图0，未提交请求、未授权生成、未准备后态。

先看 [完整正常目标](complete_target_gray_REVIEW_ONLY.jpg)、[正常双掌/X](contacts_1x_REVIEW_ONLY.png)、[084左/090右同尺动作](084_passed_left_090_target_right_same_canvas_upper_hands_1x.png)、[079/084/090同尺三态](079_passed_084_passed_090_target_same_canvas_upper_hands_1x.png)。

远R肩落、肘腕下收（腕+4,+15px），近L肩肘腕回抬（腕−5,−18px）；按实际084图像定位分别解算完整骨链，骨段长度参考保留。各完整手臂使用独立连续域，掌和唯一真杆同动：R/T_H +2°、L/T_S −2°，X处T_S在前。旧轴先清除，没有连接双掌的第三杆。胸腰与完整正确084头颈回弹，头部规模1、随胸肩回转−1.5°；未贴079姿态或旧头。

唯一四输入在 `inputs/`：完整目标、同姿双掌X三倍、脸发/衣料/鞋身份小块（无旧整身、旧双掌或C轴）、实际完整白黑mask。完整腿鞋露出区黑、整裙与隐蔽腿根过渡白；下肢源/C源字节相同，奶奶与支持前景0变化。[正常裙根/真实mask边界](under_hem_target_left_mask_right_boundary_1x.png)、[正常支持](fixed_support_1x_REVIEW_ONLY.png)。

精确四图SHA在 `INPUT_MANIFEST.json` 和 `FOUR_INPUT_SHA256.txt`。提示词、待提交参数、施工脚本齐备；未调用图像工具。等Astra实际输入门后才考虑唯一单次生成。
