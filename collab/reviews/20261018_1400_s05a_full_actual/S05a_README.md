# S05a 完整候选实际场景渲染

固定提交 **`5c45475027bbcef20012b494153fa486f38127b6`**，在干净独立工作区 `/workspace/s05a-render-5c454750` 原样运行 `js/anim/s05a_drawn.js`。没有换回旧尾段占位、修改模块／ready／EDL／音轨，也没有重新生成S05a人物图。

- [实际MP4](S05a_drawn_full.mp4)：1280×720、24fps、60帧、2.5秒，H.264，**无音轨**。
- [实际MP4解码接触表](S05a_decoded_contact.png)：28／35／36／39／42／44／47／48／49／51／52／54／55／59，共指定14帧。`S05a_decoded/`另有各帧原分辨率PNG；接触表末两格留黑不是额外黑帧。
- [实际ffprobe](S05a_ffprobe.json)、[来源和视频SHA](S05a_render_manifest.json)、[成功日志](S05a_render.log)、[只读模块副本](S05a_source_module_readonly.txt)。

MP4 SHA256：`c864a26544abd8556a6c50db88a79c8f44a56b576cd519f3d018886e67d8ea81`，512783字节。ffprobe实际解码计数60帧，24/1、1280×720、2.500000秒。模块／drawnShot／逐帧脚本与固定提交逐字节相同。

采用同一套已验证的系统 Chromium 154 配置，仅 `use_system_chromium.cjs` 指定浏览器路径，渲染逻辑不变：

```bash
node --require /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/use_system_chromium.cjs \
  tools/js/frames.cjs js/anim/s05a_drawn.js build/astra_s05a_full \
  --fps 24 --w 1280 --h 720 --workers 4 \
  --mp4 /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/S05a_drawn_full.mp4
```

首次命令在工作区尚未检出完成时发起，找不到 `tools/js/frames.cjs`，未进入渲染；该执行次序错误已纠正并保留 `S05a_initial_checkout_race.log`。检出完成后原样重跑成功。成功日志一次HTTP404未带URL，原日志保留，不能据此说零浏览器错误。未用PIL重组或诊断图冒充真实场景渲染。

作者已实际查看14帧接触表，以及036／044／049／052／055原分辨率解码图：手机从036画面下缘进入，39／44两次可见按压，47／48保持无回应，49／51张口开始泄气，52／54半垂眼继续吐气，55／59眼睛看向画左下；49／52／55确有新的头颈肩和表情，未用044顶到结尾。画面无缺失贴图／明显黑帧。原速连续自然度与带声终审仍交Astra／Opus，本文不宣称声音或用户表演验收通过。

完整尾段采用路径已在清单记录：049／052来自 `20261018_1321_opening_tails/S05a_049_052/final/`，055来自 `20261018_1336_s05a_tail_complete/final/`。各源SHA已另加进 `S05a_render_manifest.json`，可核没有误取旧占位图。
