# S08 首46 · 仅新增043–045，首芯焰可辨门待审

固定 `837f8ab8fb02f3a013f11a9e204b6db3a56d3491`，入口 `collab/reviews/20261018_2354_s08_first46_scene/s08_first46_scene.js`，SHA256 `1fdc1279d3e65ede07e564926a132583721e447f71a57179b137de7ce8b9b5e9`。48个固定运行文件均核Git原始字节和SHA，见 [清单](fixed_runtime_inputs.json)。源码没有修改。

- [46帧静音MP4](S08_first46_1920x1080_24fps.mp4)：1920×1080、24fps、46/24秒（1.916667秒）、单视频流。SHA256 `f0963b0206d608714a44c9cfc122d71089872affba7faab875add6c14cc49eea`。
- 三张**原始无损Canvas PNG直接随片交付**：[F043](canvas_new/F043.png)、[F044](canvas_new/F044.png)、[F045](canvas_new/F045.png)，与实渲输出/合片前PNG字节相同；[校验和](canvas_new/SHA256SUMS.txt)。
- [042→045实际解码全帧](00_actual_042_045.jpg)、[火根6倍近图](01_flame_root_actual6x.jpg)、[眉扬与眼神3倍](02_brows_and_eyes_actual3x.jpg)、[手/侧管/低杆座/单盒](03_hands_pipe_lever_box_actual.jpg)。4张完整解码PNG在 `decoded/`。

只一次实际新渲043–045、一次编码；000–042逐字节复用已核首43原PNG `119e98a561a7b6428b08a9b0b12b357c8b0ee6af`，见 [43帧复用清单](reused43_baseline.json)。**046不含**，旧43帧没有重渲。

## 实际观察：不能以非零公式签芯火可辨

已实看原始F043和四帧实际MP4解码及局部。043起手、火根与灯内的暖光确实增亮，眉扬仍清楚；044/045继续变亮，但眉眼、指节轮廓没有被大块白光吞掉。侧管前后、远握位、低杆座、单盒及薄影稳定。未见分离双团/畸形双尖，热白芯与亮晕增加。

**043首芯焰独立可见门未签通过：**柴火与芯火同根、同相位包合，6倍实际解码近图仍难独立辨出一股小芯焰；视觉主要读到暖光起升。源码043芯火非零不能冒充实际已辨认。交Astra裁定这一读法能否接受或另调芯火表现。本包没有擅改冻结入口或全局时间。见 [作者实看记录](author_actual_review.json)。

[源码辅助回归](source_contract_check.json)：旧43帧172个子采样合同一致，043前wick恒0；只芯火曲线采样t+1/24，match、flicker、globalt不移。043/044/045的w约.099773/.210459/.305556，[固定源参数](source_WICK_IGNITION_043_045.json)保全。仅作辅助，不代画面。

原层043 arms可见RGBA/alpha与041完全同，body alpha同041；盒1665可见像素/alpha一致、底970，低杆盘148像素RGBA一致。全46帧源PNG和相应视频解码逐一核对，最大RGB MSE=9.458479881286621，见 [验证](verification.json) / [ffprobe](ffprobe.json)。局部蓝色/热白像素计数只是诊断，不能据此判断芯火可见或整体过曝。

## 实渲与网络

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first46/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261018_2354_s08_first46_scene/s08_first46_scene.js build/S08_first46_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.7916666666666667 --to 1.9166666666666667
```

启动shim只指定系统Chromium并记录实际URL/状态、console location和原始Canvas SHA，没有改渲染逻辑。[实际网络记录](actual_network_events.jsonl)、[摘要](actual_network_summary.json)、[原始日志](increment_command.log)保留；新增三层在两个工作页6次响应均200，0pageerror/0requestfailed。本轮实际控制台404的location明确为 `/favicon.ico`，原始response事件列表未捕获该请求的404响应，按这一区别记录，不宣称全资源200；首41历史404仍URL未知，不用本轮倒推。S08生图0；未改S12/S24、EDL、音轨、ready或生产主分支，未启动全片/Blender/新付费API。
