# S08 首27帧实际Canvas · 交Astra增量审

[实际静音MP4](S08_first27_1920x1080_24fps.mp4)：**27帧 / 1920×1080 / 24fps / 1.125秒**，SHA256 `7657aca76ec5402859658385e8ee7002c6dc7d029ae8262ce7886efdaf2473bd`。只含000–026，未渲027以后、未延长停帧、未渲全片。固定源 `a4b00a05c88b3cc46284b45d1d25cff4c7ca0831`，入口SHA `4a4708868c12a2b3937d87c063a5c4c08dc053a6c6ef6745fcf9d6c3bd0b8896`。本轮一次实际Canvas渲染，没有新生图/改画或更改源模块。

[022/023/024/025/026实际解码](00_requested_actual_decodes.jpg)、[整臂与前唇](01_whole_arms_table_front_actual.jpg)、[真实握座/杆/罩2倍](02_real_grip_rod_globe_actual2x.jpg)、[火根3倍](03_match_head_actual3x.jpg)、[单盒/贴底影与前唇3倍](04_box_front_contact_actual3x.jpg)均已实际打开查看；5张全尺寸解码PNG在`decoded/`，新增4张无损Canvas PNG在`canvas_new/`。

- 022空手尚未扣住；023/024原指围住高杆，真实独立黑杆座在指后透过握座可见。025/026连同真指和杆移到中杆，同时罩环上升，未先升后压。机械合同角−.85→−.6、lift0→.5、罩升41.621621622px；此升幅为固定合同，不冒称图像精确量测。实际握座中心的本地2×2 alpha仅`[[2,0],[0,1]]`，合同邻接2×2的`[[0,2],[23,0]]`也核对了，未烘进旋钮。
- 023→025真实火根(1070,791)→(1076,794)，同帧(+6,+3)，原光火跟随；实际解码可见火焰仍在柴头，灯芯始终0。本包没有点芯。
- 盒1665可见像素仍只画一次，023/025的盒alpha及可见RGBA逐像素同017、底行970；body/arms里重盒alpha0。前唇函数逐字节同前23，实际盒与前唇原位、接触及肘前后顺序保持。

[旧23逐帧无损对照](old23_all_exact_comparison.json)：旧交付`3703140f3ca7b1a676fd0037c4c04f6064b949af`的000–022缓存全部先核原SHA，再与新27的对应PNG比，**23/23 PNG文件逐字节同**。旧d607源没有另重渲；本次a4首27按授权包含000–022。不是拿MP4有损解码作无损基准。

[实际27帧核](actual27_validation.json)、[ffprobe](ffprobe.json)、[实看记录](AUTHOR_REVIEW.json)齐：27张原Canvas PNG与27张MP4解码顺序逐一核，最大MSE9.45612；27份runtime源逐SHA和固定Git blob核、共享代码/背景/renderer字节未动。新4态源与解码均保全。这是首27帧的局部实际门，仍待Astra原速主观审，不代表027以后、完整S08或音轨/ready。

复现前检出固定源a4b00a05，并用`tools/system_chromium.cjs`选择系统Chromium（仅进程配置，固定源未改）。实际命令：

```sh
NODE_OPTIONS='--require /tmp/s08_first27_system_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261018_1900_s08_first27_scene/s08_first27_scene.js build/S08_first27 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first27_1920x1080_24fps.mp4
```

Node24.19.0、Chromium154.0.8037.57。实际stdout为27帧、1920×1080、24fps、2页面；完成时24/27约1.8帧/秒，输出上述MP4。启动有一条HTTP404控制台行，原工具未带URL，未据此猜测来源；没有pageerror，入口与实际素材、帧数及无损前缀核均通过。

交付仅写`collab/reviews/cloud_s13_20261018/render_assist/s08_first27/`，独立分支`cloud/s08-first14-render-20261018`。不改共享主分支、灯helper、Opus实现、留言、EDL、音频或ready。
