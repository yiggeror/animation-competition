# S10：ac8a7d81 六图同位必要修色，实际120帧

[实际 MP4](S10_semantic120.mp4)：1280×720 / 24fps / 120帧 / 5.000秒，无音轨。SHA256 `4f178f2c1d8486303e26f8db1ffaf04f68c1b52b59f22d73d039bf303fd494d4`。

固定 `ac8a7d8151d02788acff03ab975585905ec15c3b`，沿原 `frames.cjs` 与系统 Chromium 重渲 `js/anim/s10_drawn.js`。027/030/033/045/072/096六图 SHA 与固定作者 manifest 全部相符；模块相对该提交父版逐字节相同，曝光、机位与光照保持。前后全部登记源码和图像 SHA 未变。

[实际解码九帧缩览](actual_contact.jpg)、[原尺寸解码](decoded_actual/)、[六张修色图脸颈原尺寸近图](six_corrected_faces_native.png)。包含八起帧000/024/027/030/033/045/072/096及119，均已实看。眼影、唇下阴影和下颏原有明暗仍可读，未见明显新增色块、整脸增亮或头颈轮廓异常。尾段随原场景光变暗，不将各时刻的受光差异当成材质跳色；119维持末态。

八张角色图全部 HTTP 200，[完整逐请求记录](resource_observations.json)与[原始日志](render.log)。唯一404为 `/favicon.ico`，绘图、背景、字体和模块资源无404。

[来源及前后SHA核对](source_manifest.json)、[视频信息](actual_video_manifest.json)、[ffprobe](ffprobe.json)、[渲染命令](render_command.txt)、[可重放解码脚本](decode_actual.py)。原始120张渲染PNG保存在 `/workspace/semantic-color-render-ac8a7d81/build/s10_semantic120/`，逐帧SHA附在本目录。

本次新图像调用0次，未改色、模块、helper、曝光、机位、光照、音频或ready。交Astra统一整合，未代替最终过门。
