# Opus f68d49a 试片工具：实际运行复核

## 已复现的字幕缺失

原工具 `tools/review_film.mjs`，代码 SHA256 4ba822aa90253c2842b05af2748bc923f6756de353fe0ddd99897c97f0433cc3。只取已有、已审 S02/S05 各4秒片，输入来源见 source_manifest.json；没有重启角色渲染或制作新动作。

在隔离目录执行：

```sh
node tools/review_film.mjs --src clips --audio /tmp/laidian-audio-final-no-extra-click/film_mix_norm.wav --out /tmp/laidian-review-tool-check/phone_review_8s.mp4 --only S02,S05
```

ffmpeg 对 S02 报 `Stray % near ''`，对 S05 报 `Stray % near '，手指狂按，屏幕黑'`；每段均再重复95次。进程仍返回成功并输出8秒192帧视频，所以只看退出码会漏掉此问题。实际1秒/5秒帧已看：黑底存在，剧本字幕整行缺失。

原因是 drawtext 默认把 `%` 当作文本展开语法，EDL文字里的`2%`/`1%`被解析。最小补丁为在drawtext参数增加`expansion=none`，保留原文本，不改用户剧本。见 caption_percent_fix.patch。仅修改/tmp里的候选副本；主仓Opus实现未改。

同一输入用候选副本再次实跑：没有上述警告，S02/S05画面均已实看，镜头号、中文、2%/1%完整显示。修后8秒192帧视频全量解码通过。输出总容器8.021333秒（AAC尾部），视频轨8.000秒；这不是新剧情动作验收，也没有试听。

## 接口和纳入范围

工具当前真实入口是 `node tools/review_film.mjs`，不是留言写的 `tools/film.mjs --review`（此提交未修改film.mjs）。声音时轴在跳过镜头之前累计EDL，切S02/S05仍分别取母带12秒和30秒位置，代码逻辑正确；此处尚未做主观声画听审。

当前“有画面”判据只有`mod`和同名MP4存在。主分支合并后31项都有mod；若缓存目录留下早期占位视频，仅按当前EDL不能识别其真实来源。下一次对用户交付需固定可用片清单与源hash/渲染版本，显式排除旧占位缓存；这是来源校验缺口，不声称本次两支输入含占位。

该工具`-r 24`会重采样输入，不能把12fps片输出24fps称为真实24帧动作。此次输入本来就是已核真实24fps，不存在这一问题。字幕目前覆盖画面底部92px，建议考虑画外标注条以免遮手脚接触证据；此项是建议，不是当前已证实剧情遮挡错误。

## 证据

- S02_caption_frame.png / S05_caption_frame.png：原工具实际输出帧。
- S02_caption_fixed.png / S05_caption_fixed.png：候选一行修复后的实际输出帧。
- caption_percent_fix.patch：供Opus独立采用的最小补丁。
- source_manifest.json / output_probe.json：来源与原输出轨道参数。
