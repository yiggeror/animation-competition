# S03a 实际场景渲染协助

按补充委托，固定 `f4f0ea430467d111055dffa4e47620a2def795f7`，原样运行 `js/anim/s03a_drawn.js`。**本包确为项目 Chromium 渲染器输出，不是PIL重组或人物替代诊断。** S03a模块、逐帧脚本、场景资源均未改；未渲S05a，未写ready.md、EDL或音频。

- [实际MP4](S03a_drawn_full.mp4)：1280×720、24fps、36帧、1.5秒，H.264。此次按逐帧脚本输出，**无音轨**，不作声画通过结论。
- [实际MP4解码接触表](S03a_decoded_contact.png)：F000／008／014／017／021／023／025／028／035，另有 `decoded/` 九张原分辨率解码PNG。
- [实际参数](ffprobe.json)、[模块及九源图SHA](render_manifest.json)、[成功日志](render.log)、[首次启动失败日志](render_initial_missing_browser.log)。

MP4 SHA256：`72192dfe68ac54a32718b443520e1ab529bd6280b27daad2c69e4b83366614b1`，120134字节。ffprobe实际读到36帧、24/1、1280×720、1.500000秒。

环境已有Playwright 1.62.1与系统Chromium 154.0.8037.57，但没有Playwright默认缓存的headless shell。第一次直接运行报“Executable doesn't exist”，没有产出视频；原错误保留。随后仅通过 `use_system_chromium.cjs` 将 `chromium.launch` 的可执行路径指定为 `/usr/bin/chromium`，其他参数和渲染逻辑不变；没有下载浏览器或安装新依赖。

在固定提交的干净独立工作区 `/workspace/s03a-render-f4f0ea43` 实际执行：

```bash
node --require /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/use_system_chromium.cjs \
  tools/js/frames.cjs js/anim/s03a_drawn.js build/astra_s03a_full \
  --fps 24 --w 1280 --h 720 --workers 4 \
  --mp4 /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/S03a_drawn_full.mp4
```

实看记录：已看解码九帧总览及F014／021／023／028大图；背景、人物与前景手瓜均实际出现。F008手瓜已进入，F014开始转，F017／021／023整头转开，F025回转，F028／035回正且嘴仍轻撅；下胸位置与手瓜落点未出现显著跳位。021→023发尾有变化，未用017单图顶8帧。未见缺图／黑帧；这是本次渲染和抽帧的作者检查，不代Astra独审、原速表演或带声终审。

成功日志中有一次HTTP404。该条未携带URL；可见九态与资源SHA已经核对，仍把原日志完整保留，不将其擅自改写为“零浏览器错误”。

原始逐帧PNG36张留在固定渲染工作区 `build/astra_s03a_full/`，本包交压缩MP4及从它实际解码的指定帧。技术校验不能替代最终连续观看。
