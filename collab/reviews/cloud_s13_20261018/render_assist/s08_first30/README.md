# S08 首30帧 · 复用27＋新增3实际Canvas

[实际30帧静音影片](S08_first30_1920x1080_24fps.mp4)：1920×1080/24fps/1.25秒，SHA256 `86aa602b56408d4a9b3e3022ebb9120ea0016e5b18d816f9dd39d9adfebf8a96`。固定源 `25705ee43f0a7e169cd9cc4ba05d50a341d6f3b1`，入口SHA `1f4c6c48e331f4e97c1ae1f9f98cf6a09e88c7e6e4183644e9a116e37b2a5f58`。

**复用000–026的27张已核无损Canvas PNG，只新实际渲027–029三帧，再编码30帧。没有声称全30重渲。**27缓存逐SHA重新核对9a6b01f7的原actual27账本，复制后仍逐字节同。新增`build/S08_first30_increment`恰为00027/00028/00029三PNG。030以后没有制作或扩渲。实际命令成功，环境可执行。

[026→027/028/029实际解码全图](00_requested_actual_decodes.jpg)、[25–29真实低杆握座及升罩2倍](02_real_low_grip_rod_globe_actual2x.jpg)、[真火根3倍](03_match_head_actual3x.jpg)、[单盒/原接影3倍](04_single_box_original_contact_actual3x.jpg)、[整臂与前唇](01_whole_arms_table_front_actual.jpg)已实看。全尺寸解码026–029在`decoded/`，新3张无损PNG在`canvas_new/`。

027原指随低杆到位，真独立黑杆座从透明握座后读得出；罩环与人物/杆在同027帧升起，029仍扣低杆。合同低杆角−.35、lift1、端点(1233.953205,766.894374)、总罩升83.243243px；这些数值是固定合同，不冒称图像精确量测。实际火根(1082,797)、可见木出口(1054,834)，相025前进(+6,+3)，火焰仍在柴头、灯芯0。盒1665可见像素只一份，原alpha/可见RGBA同025、底行970，原薄影/前唇保持。实际局部视觉门成立，仍请Astra原速审。

[完整实核](actual30_validation.json)与[ffprobe](ffprobe.json)：复用27、新渲3、30源帧→解码顺序及最大MSE9.45261、30份runtime SHA/固定git核、独立握座2×2 alpha `[[0,2],[23,0]]`、单盒与互斥层均保全。[static_regression_run.json](static_regression_run.json)是另列的静态/绘制指令回归：前27的108子帧合同、27帧绘制光火、24旧PNG与原函数文本一致；不把该记录当实际Canvas结果。作者测试脚本复制到本包，仅适配相对导入与输出目录，断言逻辑不变，固定源未写入。

实际新增命令：

```sh
NODE_OPTIONS='--require /tmp/s08_first27_system_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261018_1940_s08_first30_scene/s08_first30_scene.js build/S08_first30_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.125 --to 1.25
```

随后从`build/S08_first27`复制000–026，从increment复制027–029到`build/S08_first30`，ffmpeg按24fps/crf18/tune animation编码30帧。无音轨，无新图像调用，未改画/灯helper/场景源/留言/EDL/ready。首30局部验收不代表完整S08。
