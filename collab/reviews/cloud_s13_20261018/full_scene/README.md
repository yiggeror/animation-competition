# S13 十六态 · 真实 Canvas 场景候选

优先看 [真实场景片](S13_drawn_120f_720p24.mp4)、[实际解码十六态](qa/00_all16_decoded_scene.jpg)、[闭口/起转/落定边界](qa/01_closure_turn_settle_boundaries_decoded.jpg)、[尾段曝光](qa/02_tail_timing_decoded.jpg)。**1280×720 / 24fps / 120帧 / 5秒，真实Chromium Canvas与共享`renderPaint`灯光管线，无音频。** 作者已实看这些实际帧；完整场景候选待Astra终审，未登记ready，未接EDL或音轨。

[专用模块候选](s13_drawn.js)导出`DURATION=5`、`SHEET`、`pick(t)`、`state(t)`及`renderFrame`。人物只按曝光切换十六张实际画稿，统一`.85+(330,−30)`，没有旧A/B、mouthScale、脸部搬移、变形或溶解。房间/木箱、虚焦鹤与灯光函数逐字继承原S13固定源，机位不动，灯光只经`renderPaint`乘一次；来源和十六张SHA见[场景清单](qa/scene_source_manifest.json)。

完整曝光：`0×18,18×6,24×6,30×6,36×4,40×4,44×6,50×8,58×10,68×10,78×6,84×3,87×3,90×4,94×6,100×20`。F084–086明确闭口且不转，F087才整头起转；F094头到位、自由发尾滞后，F100尾落定后保持到119。两手始终画外，未增加捂嘴手。

[全120帧验证](qa/actual_120f_scene_validation.json)：MP4独立解码后逐帧对照渲染PNG，全部120帧顺序匹配；归一化人物ROI的十六态分类也全匹配。编码对原Canvas最大均方误差10.069（8位通道），不冒称无损或逐位相同。[原Canvas120帧哈希](qa/rendered_120_source_frame_hashes.json)、[ffprobe](qa/ffprobe.json)及八张关键实际解码PNG同目录保留。

[浏览器核验](qa/browser_audit.json)另外实渲十六关键态、检查全部120个选图结果，无必需资源404或pageerror；唯一404为`favicon.ico`。默认Playwright浏览器文件不存在，经单项启动检查确认系统Chromium可用，仅用[本进程启动配置](tools/use_system_chromium.cjs)指定`/usr/bin/chromium`。仓库`frames.cjs`、`dev/view.html`、`paintshot.js`及其他共享代码未改；未安装新依赖或浏览器。实际运行Playwright1.62.1 / Chromium154.0.8037.57。

复现（仅此5秒镜头，输出在本独占目录和`/tmp`）：

```bash
bash collab/reviews/cloud_s13_20261018/full_scene/tools/render_scene.sh
node collab/reviews/cloud_s13_20261018/full_scene/tools/audit_browser.cjs
python3 collab/reviews/cloud_s13_20261018/full_scene/tools/check_scene.py
```

整合时可将模块原样放到`js/anim/s13_drawn.js`：`/js/...`绝对Web导入与SHEET中`/collab/reviews/...`路径在仓库静态服务器可用；若Astra将素材移入`assets/chars`，相应更新SHEET。此候选保留审查路径，不自动修改公共模块、EDL、音频或ready。
