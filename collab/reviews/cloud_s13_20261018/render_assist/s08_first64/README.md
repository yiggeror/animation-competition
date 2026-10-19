# S08 首64 · 只增061–063实际Canvas

固定源`88262d20d13c1901d41bf265242d93895f046670`；入口`collab/reviews/20261019_0236_s08_first64_scene/s08_first64_scene.js` SHA256 `3e4bf3c086aab094b8c721db30e6a76e929f88a9412819fff4d406d7c5411100`。60项实际运行文件渲前核SHA/Git字节后即启动；79路径补充读回及渲后/静态审计后复核，不为非运行文件延后渲染。源文件未改。

- [64帧实际无声片](S08_first64_1920x1080_24fps.mp4)：1920×1080、24fps、64/24秒，单视频流，SHA256 `db4d8b5bfeb2ea6eb7a7e30530e64b1700d74aec32b91028383307b8fe69ae6e`。
- 新原始无损Canvas：[F061](canvas_new/F061.png)、[F062](canvas_new/F062.png)、[F063](canvas_new/F063.png)，[完整SHA](canvas_new/SHA256SUMS.txt)。实渲输出、浏览器PNG SHA、合片源PNG与交付图全同。
- [060→061→062→063实际解码](00_actual_060_063.jpg)、[新药头烟根/芯火4倍](01_smoke_root_wick_actual4x.jpg)、[双臂层次/低杆/单盒影2倍](02_hands_low_lever_single_box_actual2x.jpg)；四张完整解码PNG在`decoded/`。

只1次实际渲061–063、1次编码。旧000–060按`a2938aba7d367c957188799c1beccc339949cea8`首61原Canvas逐SHA并复制后核字节复用，[清单](reused61_baseline.json)。未重渲旧帧，未渲064+，没有新生图。合片脚本首次预检因本云复制模板旧目录名而停在复制/ffmpeg之前，只有两个空目录，修本目录名后完成一次编码；未重做实际增量，[记录](assembly_preflight_note.json)。

实看060→061整前臂/腕掌下带连续、尚未触桌；烟根改随真实药头`(1310.1876968280087,879.6050802415948)`，061–063灰细烟向上弯动，旧位无残根；固定芯火不断，火柴未复燃。单盒/贴底影、远单镯手/透明低杆座、近臂前后层次保持。[实看记录](author_actual_review.json)。

[验证](verification.json)：64个源PNG逐帧与实际视频解码比较，最大RGB MSE `9.87852001`；[ffprobe](ffprobe.json)确认64帧1080p24无声。静态辅助244个旧子样/54旧层SHA/原光火烟ctx回归通过，不替代实际图像。

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first64/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0236_s08_first64_scene/s08_first64_scene.js build/S08_first64_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 2.5416666666666665 --to 2.6666666666666665
```

[命令原日志](increment_command.log)、[实际资源日志](actual_network_events.jsonl)、[摘要](actual_network_summary.json)、[成功加载文件固定Git读回](observed_runtime_fixed_bytes.json)。061三层在两页6响应均200，0pageerror/0requestfailed；实际favicon404 console URL原样保留，未声称全部请求200。

独立私有分支`cloud/s08-first64-render-20261019`基于固定源，只交本目录。不改共享实现/留言/ready/EDL/声音，不推共享主分支。S12工作在另一个工作树/私分支交付，不含在此包。
