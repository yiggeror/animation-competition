# S03a 新冠发修色＋资产迁移：固定 f17651aa 实际 36 帧

[实片 S03a_color36.mp4](S03a_color36.mp4)：1280×720、24fps、1.500 秒、36 帧、无音轨。MP4 SHA256 `9d2277ec84b2b5b394614c4055175d606fc8eb18f7ed29771df985b6ed3436f1`。

固定源码 `f17651aaee6f03cf0e48bd2939c4c6c1fb86cffb`，`js/anim/s03a_drawn.js` SHA `cf9d029876a31829c20d68757c346839601134177acbf60790ec89856e6fd3cf`。沿原 `frames.cjs` 和系统 Chromium 配置，从 0 到 1.5 秒重新实渲；九张迁移状态图及前景手瓜共十项 SHA 和源码前后不变检查见 [source_manifest.json](source_manifest.json)。

- 已从实际 MP4 解码 `000/008/011/014/017/021/023/025/028/035`：[十帧缩览](actual_contact.jpg)、[原尺寸解码](decoded_actual/)、[14→17→25 冠发原尺寸近图](crown_014_017_025_native.png)。均已实际打开检查。
- 14→17→25 未见明显冠发跳色。同一内部发色框 `(640,180)–(662,202)` 在解码图的 RGB 中位数分别 `(44,33,30)` / `(44,34,31)` / `(44,33,30)`；这是实片观察，不把不同姿态的同坐标像素当成同一发丝。
- 全部十项 `assets/chars/x03a/` 图及房间背景在主渲染中实录 HTTP 200，[资源记录](resource_observations.json)。原始 [render.log](render.log) 保留一条未署路径的 404；只读补查实际请求确认是 `/favicon.ico`，[完整服务端请求补查](resource_probe.json)。绘图资源无 404，无失败请求。

[命令](render_command.txt)、[ffprobe](ffprobe.json)、[视频信息及 SHA](actual_video_manifest.json)、[解码脚本](decode_actual.py)、[只读资源补查脚本](probe_resources.cjs)。原始 36 张渲染 PNG 保存在 `/workspace/s03a-color-render-f17651aa/build/s03a_color36/`。

本次没有重生或修色调用，未改模块、共享 helper、音频或 ready；只交实际片和核查材料。Astra 统一整合。
