# S08 首58 · 只新增053–057实际灭柴与余烟

固定源 **`3e5584634257dd9aca95aeba7273ddc643ea6351`** 已从origin取回，源包 **68/68文件** 渲前及渲后/静态审计后逐字节核Git，[读回](fixed_packet_readback.json)。入口 `collab/reviews/20261019_0134_s08_first58_scene/s08_first58_scene.js` SHA256 **`77c1afd1bc96cae54dbe0f9c9c0319a7fe3e09cdb466d294bc51a40ed3133e93`**，54项运行行表见 [清单](fixed_runtime_inputs.json)。源文件未改。

- [58帧静音实际片](S08_first58_1920x1080_24fps.mp4)：1920×1080、24fps、58/24秒（2.416667秒），单视频流，SHA256 **`48ddec9f89b4a415b07a8182a0a8a247f4042be8e3fa32eec46223c6de0601cf`**。
- 新五张原始无损Canvas直接交：[F053](canvas_new/F053.png)、[F054](canvas_new/F054.png)、[F055](canvas_new/F055.png)、[F056](canvas_new/F056.png)、[F057](canvas_new/F057.png)，[五张完整SHA](canvas_new/SHA256SUMS.txt)。与实渲输出、合片前PNG及浏览器PNG SHA相同。
- [052→057实际解码全帧](00_actual_052_057.jpg)、[灭焰/药头烟根/固定芯火4倍](01_extinction_smoke_root_actual4x.jpg)、[双手侧管/低杆/单盒2倍](02_hands_pipe_low_lever_single_box_actual2x.jpg)、[眉眼3倍](03_brows_and_eyes_actual3x.jpg)。六张完整MP4解码PNG在 `decoded/`。

只1次实渲053–057、1次编码。旧000–052按首53交付 **`51bb229998fd8c8a407b09d2156b5df764de4d3e`** 的原始无损PNG逐SHA复用，合片复制后核字节全同，[53帧复用清单](reused53_baseline.json)。**不含F058及以后**，没有重渲旧53帧，没有新生图。

## 实际检查

实看原始053/057及052→057实际视频解码与局部：052柴焰仍亮，053药头处明火及贴近手部的额外亮晕退去，灰细烟从真实药头(1350,782.572973)起；没有在旧悬空位置留火或生烟。054–057细烟向上延伸弯动，057余烟仍读得出。固定芯火继续独立燃烧，未随灭柴闪断。烟表现依据真实Canvas/MP4，而非只据公式非零。

近手柴/侧管前后、远单镯手与低杆透明座、桌盒单份和薄贴底影稳定，人物继续精确复用051/046整组原图，没做代码人物或孤手变形。[作者实看记录](author_actual_review.json)。

静态辅助核旧53的212个子采样、51份旧原层字节/绘制/照明/火光相同；从053停match emit/light/glow，芯火幅.55；三stroke烟沿原公式，起点接真实药头，时钟未移。[结果及五帧公式字段](static_TEST_RESULT.json)不替代实际光栅化。静态测试写报告重定向到本独占目录，源68文件保持原字节。

全58帧源PNG逐一对视频解码，最大RGB MSE=9.942446，[验证](verification.json)、[ffprobe](ffprobe.json)。Canvas原图与有损解码明确分开。

## 命令与实际资源日志

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first58/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0134_s08_first58_scene/s08_first58_scene.js build/S08_first58_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 2.2083333333333335 --to 2.4166666666666665
```

[命令原日志](increment_command.log)、[实际URL/状态/console位置](actual_network_events.jsonl)、[摘要](actual_network_summary.json)、[实际成功加载文件核固定Git原字节](observed_runtime_fixed_bytes.json)。复用046三层在两页6次响应均200，0pageerror/0requestfailed；实际favicon404 console URL保留，response事件未捕获该响应，不称全部请求200，不倒推历史未知404。

只交独占目录并同步私分支；不写生产分支、共享实现/留言、ready、EDL或声音。S12待办未在此包修改，018未启动；未渲全片/旧帧/058+，未用Blender或付费API。
