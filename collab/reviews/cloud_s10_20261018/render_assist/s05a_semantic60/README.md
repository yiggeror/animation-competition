# S05a：ac8a7d81 必要修色＋尾图迁移，实际60帧

[实际 MP4](S05a_semantic60.mp4)：1280×720 / 24fps / 60帧 / 2.500秒，无音轨。SHA256 `b8d1451eeb7aa8491d895dbfa2c8a9053560041810a340fa3c552aa1b5ca7374`。

固定 `ac8a7d8151d02788acff03ab975585905ec15c3b`，沿原 `frames.cjs` 与系统 Chromium 重渲 `js/anim/s05a_drawn.js`。四张修色图 SHA 与固定作者 manifest 全部相符；相对该提交父版，模块只有 T/L 路径改动，曝光、机位、光照不变，047仍复用044。

[实际解码15帧缩览](actual_contact.jpg)、[原尺寸解码](decoded_actual/)、[重点七帧脸部原尺寸近图](tail_faces_native.png)。包含指定042/044/047/049/052/055/059，均已实看。未见明显肤色断跳；纵向肤色渐变、原下颏和眼周明暗仍可读，未表现为整脸平涂。047与044的复用姿态一致，049→052→055泄气过程可读；059保持055。

实际使用的13张图全部 HTTP 200，迁移尾图均从 `assets/chars/x05a/` 读取；[逐请求记录](resource_observations.json)与[原始日志](render.log)。唯一404为 `/favicon.ico`，绘图、背景、字体和模块资源无404。

[来源及前后SHA核对](source_manifest.json)、[视频信息](actual_video_manifest.json)、[ffprobe](ffprobe.json)、[渲染命令](render_command.txt)、[可重放解码脚本](decode_actual.py)。原始60张渲染 PNG保存在 `/workspace/semantic-color-render-ac8a7d81/build/s05a_semantic60/`，逐帧SHA附在本目录。

本次新图像调用0次，未改色、模块、helper、曝光、机位、光照、音频或ready。交Astra统一整合，未代替最终过门。
