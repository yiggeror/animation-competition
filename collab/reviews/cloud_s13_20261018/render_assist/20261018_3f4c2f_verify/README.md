# 固定3f4c2f18 · S08首帧与S10迁移实渲验证

固定提交`3f4c2f187daaeacc6b26e26260e426823f2fa6ad`，临时干净检出`/tmp/s13_render_assist_3f4c2f`。没有生图、修改人物/场景/桌沿、全镜重审或音频改动；交付仅本新子目录。Playwright1.62.1 / 系统Chromium154.0.8037.57，仓库snap/serve/dev/paint管线原字节运行。

**S08：实际PNG已交，但两肘尖被原桌前沿遮掉，需协调裁定。** 看[1920×1080原始实帧](S08/S08_F000_actual_1920x1080.png)、[肘部原母态/实帧近图](S08/elbows_actual_vs_locked_art.jpg)、[双手道具/灯近图](S08/hands_lamp_actual_vs_locked_art.jpg)。c803母态和x0/y0/sc1均核对；无火，灯底`(1415,965.6)`、原桌前沿y981保持。双手、火柴和盒在灯左侧，远手与拨杆有可见间隙，未见手中道具与玻璃/灯座穿插。近肘下缘被前沿部分遮掉，远肘下缘明显截平；不把此构图问题签为通过，不自行改桌。

[S08资源/遮挡检查](S08/render_resource_and_elbow_checks.json)：snap实帧与独立同帧Canvas探针逐字节相同；原桌alpha与母态肤色的诊断交集近肘549像素、bbox`[762,979,806,997]`，远肘430像素、bbox`[1039,979,1086,991]`。y979起是原前沿笔画覆盖，名义桌边仍y981。此统计为辅助定位的颜色启发式，视觉结论见实际近图，不是骨点测量。

S08执行原命令（固定检出根目录）：

```bash
node --require /workspace/animation-competition/collab/reviews/cloud_s13_20261018/full_scene/tools/use_system_chromium.cjs tools/js/snap.cjs /collab/reviews/20261018_1606_s08_f000_scene/s08_f000_scene.js /tmp/S08_F000.png 1920 1080 0
```

**S10：新旧0/24/27/30/33/45/72/96八帧，1920×1080，8/8实际PNG逐字节相同，解码RGBA最大差0。** [实际八帧接触表](S10_actual_8_checkpoints.jpg)，原PNG分别在`S10_new/`和`S10_old/`。[完整渲染、SHA与资源记录](S10_render_and_resources.json)、[像素检查](S10_pixel_checks.json)、[八组迁移资产原字节映射](S10_adopted_asset_byte_map.json)齐全。新`js/anim/s10_drawn.js`和旧候选分别在真实浏览器Canvas执行，未合成对照占位图，未重渲全120帧或重审表演。

两镜所有必需资源均HTTP200，浏览器原生fetch取得的字节SHA等于固定检出文件、git blob；无pageerror或请求失败，favicon.ico404单列忽略。首次DevTools读取大字体/位图响应体发生inspector缓存淘汰，已改用浏览器原生fetch核SHA，[方法记录](audit_method_note.json)明确保留；未改素材来掩盖诊断问题。

复查入口在本目录`tools/audit_s08.cjs`及`tools/render_s10_pair.cjs`，参数传固定检出根路径。`system_chromium.cjs`只配置进程内浏览器路径。S08仍只F000；S10只迁移检查，不代完整场景/音轨新验收。
