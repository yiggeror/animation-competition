# S07 固定abc2059完整108帧实际接景渲染

实际MP4：S07_full108_abc2059_1920x1080_24fps_ACTUAL.mp4。108帧、24fps、1920×1080、4.5秒、无声，SHA256：0e6e920725928095ded816b5e59939dee2d07618d792344ea10df38ce2a90789。build/S07_full108.mp4逐字节相同。此包只交实际渲染与审查证据，不修改生产实现，不签ready/EDL/audio。

固定源提交abc2059eb84adb74e39958a7105441257fc52115，独立分支cloud/s07-full108-render-20261019-abc2059。已完整读取collab/reviews/20261019_0650_s07_full108/README.md，其原文快照为FIXED_SOURCE_README.md。执行原命令：

```sh
node tools/js/frames.cjs js/anim/s07_drawn.js build/S07_full108 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S07_full108.mp4
```

仅环境适配：NODE_PATH指向预装Playwright，NODE_OPTIONS预加载本包capture_browser_resources.cjs。默认缓存Chromium不存在，因此用系统/usr/bin/chromium154.0.8037.57；该适配器只选择浏览器并监听资源，不改变模块/机位/人物/灯光。完整命令与原文件前后SHA在source_before_render.json及actual_render_and_decode_checks.json。

原渲染108张PNG保留于忽略目录build/S07_full108。按固定README要求，从最终MP4真正解码32张边界：000/015/016/024/025/037/038/039/053/056/057/061/062/067/068/072/073/078/079/083/084/089/090/094/095/099/100/102/103/105/106/107，全部1920×1080原帧在decoded_actual_mp4。四张总表和056→057、099→100、103→106同框/细节在boundary_sheets，均已实际打开检查，未拿结构测试替代画面。

实际发现：056→057为既定小满近景切全景，后续锁定步态及脚底投影可见，未见缺人或缺景资源。099→100仍只有一盏暗灯，没有观察到双灯叠画；但原灯右侧火柴盒在100起消失，明确见ACTUAL_F099_F100_matchbox_continuity_3x.png及解码099/100。固定源码tableLamp同时绘制火柴盒（js/anim/s01.js:56），F100停整个旧灯层时一并停掉。此为交主审裁定的连续性问题，按任务未修改实现。103→106同闭握真灯小幅抬起，脚/body稳定，原桌影仍为基线，不签提灯投影物理已过。

浏览器资源：121次记录请求/响应全部200，0requestfailed、0pageerror；仅浏览器favicon.ico有一条console404，非场景图片/脚本/字体缺失。完整事件逐行日志browser_resources.jsonl，汇总browser_resource_summary.json，渲染控制台render.log。

实际MP4、32张真正回解边界、必要对照、浏览器日志及所有文件SHA清单均随本包交付，供主审实审；不新增生图，不改生产实现或共享文档。
