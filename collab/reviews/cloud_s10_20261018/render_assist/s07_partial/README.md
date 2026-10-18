# S07 两段实际场景诊断渲染

固定 **60159846257c803263b4eab675ba35487fff12ce**，原样执行源README两条命令，只增加已验证的系统Chromium启动配置并将MP4／日志写到本目录。源模块、素材、相机／灯光／道具及音轨均未改；S07生成0次。只读源README／模块、SHA及干净工作区检查见 `source_*`。

| 实际视频 | 范围 | 帧数／时长 | 实际解码表 |
|---|---|---|---|
| [S07_first25.mp4](S07_first25.mp4) | 000–024 | 25帧／25÷24秒 | [接触表](S07_first25_contact.png)，14张指定帧见S07_first25_decoded/ |
| [S07_x39_56.mp4](S07_x39_56.mp4) | 039–056 | 18帧／0.75秒 | [接触表](S07_x39_56_contact.png)，10张指定帧见S07_x39_56_decoded/ |

两段均真实Chromium项目渲染，1280×720、24fps、H.264、无声。参数与视频SHA见 `actual_video_manifest.json` 和两份ffprobe JSON；日志保留一次无URL的404，不作“零浏览器错误”宣称。接触表来自实际MP4的ffmpeg解码，第二段绝对帧号=本段局部帧号+39。不是PIL重组的场景替代图。

作者实看两张接触表及016／018／022／039／053原尺寸解码图：

- 000／003／006／008有小满松指、手机转面／落席的换张；016切奶奶近景，018盆落下、022双手离开，盆全程只一只。凳、臀及脚／地接触在实景可读，没有据素材注册值直接宣布全动作通过。
- 039／043／046／049／053有仰躺、扇手、看向奶奶和手落席的变化，未用039静图顶满。**039和053实图中没有清晰可辨的手机轮廓**；独立手机层确实在人物后，但可能被身体／头发遮住，仍需Astra确认预期可见性。不能用源码层次正确代替这一实图问题通过。
- 镜头整体偏暗，但动作／接触尚可检查；未调整照明。原速自然度、最终光照和带声验收仍待团队终审。

**没有渲025–038或057–107，没有补画外翻身／起身／走路，也没有拼成完整108帧或写ready.md。** 本交付仅两段诊断，缺口和全镜未完成状态保持。

实际命令与源README相同的范围参数：

```bash
node --require /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/use_system_chromium.cjs tools/js/frames.cjs collab/reviews/20261018_1425_s07_partial_scene/s07_drawn_partial_candidate.js build/s07_first25 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 1.0416666666666667 --mp4 /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/s07_partial/S07_first25.mp4
node --require /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/use_system_chromium.cjs tools/js/frames.cjs collab/reviews/20261018_1425_s07_partial_scene/s07_drawn_partial_candidate.js build/s07_x39_56 --fps 24 --w 1280 --h 720 --workers 4 --from 1.625 --to 2.375 --mp4 /workspace/cloud-s10-review-20261018-1324/collab/reviews/cloud_s10_20261018/render_assist/s07_partial/S07_x39_56.mp4
```

工作区 `/workspace/s07-render-60159846` 固定源提交，未修改模块。`decode_actual.py`仅重放MP4解码／参数检查，不渲其他范围。
