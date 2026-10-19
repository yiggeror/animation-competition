# S29 060领肩斜裂：同raw零调用修复、仅补6帧、原18帧精确复用

主审已通过历史`55942c39`的动作、衣摆、远袖及054/066结构，仅要求修060右领肩实际透背景斜裂（实景约x767–798/y375–407）。本包只修该完整领肩蓝布语义域，不重生成整衣或人物，新增生图0。

## 实际结果

主审与现有只读云审均实际打开新060/065完整回解帧、两换张1:1、历史对照和24帧顺序表：原透背景斜裂已消失，肩顶未见明显新尖裂或双墨，领—肩—袖正常尺寸连续；059→060、065→066的掌压布、远夹口、同源布及真偶四杆未见新增回退。此结论只覆盖该修复及048–071局部实际序列，不登记全镜ready。

- `S29_F060_F065_ACTUAL_SCENE_1080p24.mp4`：唯一一次新场景绘制，060–065共6帧，1920×1080、24fps、0.25秒、静音。SHA256 `9a1d3a70184b39ce1df63491acc5007958df9965a27fc8bfaeb9cd61ad4d7ca9`。
- `S29_F048_F071_REUSED18_REPLACED060_065_LOSSLESS.mp4`：24帧/1秒静音复核片。原18帧解码YUV420平面直接复用，只替换上述6帧，再以H264 qp0无损封装；独立回解确认原18帧YUV和RGB全部0差。SHA256 `f1feeb4d0502c22866010a1a6462400e7a78c0be3af7a7ab696e2d59e8ed93d6`。
- `TWO_SWITCHES_SHOULDER_ACTUAL_OUTPUT_1TO1.png`：实际059→060、065→066，原输出尺度。
- `HISTORY_VS_NEW060_ACTUAL_SHOULDER_1TO1.png`：同一实景060修前/修后。
- `actual_decoded_keys/`、`ALL24_REUSED18_NEW6_ACTUAL_DECODED_CONTACT.png`：实际编码视频回解图；`keys/`为新6帧原Canvas。
- `VIDEO_BROWSER_DECODE_CHECK.json`：新6帧普通H264与重组24帧H264 High4:4:4 Predictive/yuv420p均实际在Chromium加载并解码，readyState4、1080p、0.25/1秒、error null。该次仅解码视频，场景绘制0。

历史目录`F048_F071_SEMANTIC_CLOSURE_ZERO_CALL_20261019/`原样保留，旧24帧MP4 SHA256仍为`5c8ed0c46726c8b210341b5bee74813996c2dde9a1b31800829a0ef2d69e9691`。没有重新画另外18帧或覆盖历史版本。

## 同raw完整肩布与保护

唯一图源是既有060原件：`../F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F060/originals/S29_F060_call01_RAW_UNTOUCHED.png`，SHA256 `3fc6425ff459cc279c19adbd309669ec591be06387e4f964afd0cece7a251c1e`。实际请求、逐字提示词、三输入与原始工具输出仍在原`15061c1c`归档，本轮没有新提示词提交或图像调用。

`repair_native_shoulder.py`提取该原件完整蓝布领肩，以一次连续衣面映射从锁定领口接到既有远袖注册矩阵；不是横矩形贴色或只按白像素补洞。处理包括原透明斜带和旧斜线尾。保留真实领口/颈肤及领肩外边线带、既有袖外廓，臂掌和夹点没有新变换。新完整母图`F060_COLLAR_SHOULDER_CLOSED_RGBA.png` SHA256 `b58a1241dd966774e9ff68c2ae5e05fadeca523a016b6cabecc264318c9d40c5`。

`SHOULDER_SOURCE_AND_LOCK_CHECK.json`及显式mask记录完整差域：域外0差，受保护领颈/真实袖廓0差，臂掌0差，513行以下（含衣摆、布、偶、四杆及全部手）0差。`OLD_SPLIT_CENTERLINE_ACTUAL_RGBA_SAMPLES.json`保留旧透明位置到新蓝布alpha255的实测样本。前次短叠墨观察后，最终额外锁回真实领肩顶部外边线带；最终实景已实际复核。原生衣花差异仍为已审绘张变化，不声称三态像素一致。

## 执行与核验

`render_six_only.cjs`只允许全局060–065，读取原相机、灯光、背景；4项受保护场景资源前后SHA相同，无请求/浏览器错误。`ACTUAL_BROWSER_RUN.json`记录实际6次绘制与固定整人矩阵。

`reuse18_replace6_and_decode.py`只解码并重组已有视频，不调用浏览器或人物代码；`REUSED18_REPLACEMENT6_ACTUAL_DECODE_CHECK.json`逐帧记录18复用/6替换的YUV及RGB SHA，全部与各自原视频精确一致。两份ffprobe和原stdout保全。早期一次线性alpha接边候选仅在静态自查看到颈边不合后弃用，未实渲；诊断crop及说明在`diagnostics/`，不计新生图。

本包只交Astra统一整合，未改共享生产、EDL、声音或ready。后续072/078/084仅另备输入0调用，不在此包擅自续画。
