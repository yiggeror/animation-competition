# S13 实片与手机全帧独审增量交付

本批是在 `df164df` 之后补齐的实际检查和小体积产物，不重传既存母带、人物原图或全帧解码目录。仍是局部集成候选，旧249秒粗剪未更新，不是正式成片。

## 已保存版本

独立实现分支：[codex/astra-integration-20261017](https://github.com/yiggeror/animation-competition/tree/codex/astra-integration-20261017)，S07/S13固定提交 **64ad53a8b42b8a778c51648b62112f2e095a9024**，音频修正另存 **02cb28a48d7df0d4ce4c8d0bc422e0481c91c376**。S07实现为bb9cd1c，S13实现为e90e9cd，64ad53a将两镜绑定EDL；协作资料df164df已合入独立分支。未向Opus协作分支合并实现，也未改写其留言。

[远端S13代码、helper、四层PNG、EDL读回](remote_readback/64ad53a.json)全部字节一致，四层PNG完整解码；[S07实现读回](remote_readback/bb9cd1c.json)与[上一交付关键文件读回](remote_readback/df164df.json)亦附。

## 可看产物与实际结论

| 产物 | 证据与结论 | 剩余范围 |
|---|---|---|
| [S13 5秒带声24fps](clips/S13_24fps_audio.mp4) | [作者](s13/author/report.md)、[独审](s13/independent/report.md)。真实120帧，口上暗点、颈根双线已关闭；A肩领固定，B局部头颈配准，假哈欠开合可读 | F32→33是可见两姿切换，不是连续扭头；没有独立奶奶反打/身体退回，尚未核同版前后联剪或试听 |
| [S02 4秒带声24fps](../20261017_0616_integration/phone_actual24/S02_24fps_audio.mp4) | [手机最终独审](phone_independent/report.md)，实际96帧全覆盖，四次点按及松开可读 | 未核整片承接、未试听 |
| [S05 4秒带声24fps](../20261017_0616_integration/phone_actual24/S05_24fps_audio.mp4) | 同份独审。14次亮屏连按各留1–3松开帧，黑屏后两次再试分离；旧F29/33/69/85/93指根裂缝未回归，无双拇指或拉条 | 未核同版S04→S05停电衔接、未试听 |

S13带声版仅复制独审静音视频流，配[上一批实际母带](../20261017_0616_integration/audio_final/film_mix_norm.wav)的全片70–75秒；[命令/hash/ffprobe/input测量](clips/S13_manifest.json)齐全。母带SHA256 `101d818f324f55c85c793c19b42bd774d6a8393ae67ec0565260b001bb91091e`。新MP4实测局部-17.72LUFS/-5.22dBTP，不把单镜响度要求成全片-16；没有新增哈欠声或音乐。

整片母带和31镜独立AAC的数值检验仍以[上一批audio_final](../20261017_0616_integration/audio_final)为准：WAV -16.04LUFS/-4.40dBTP，全片AAC -16.08/-3.72，31镜最高真峰-3.16；数值不等于听感通过。

## 正在完成的工作及给Opus的接续

用户已明确告知『opus限额了』并授权继续独立制作。没有催收或将无回复视为漏读。S29包布/看手机前段已有独审；准备吹灯近景及S30巨大头影尾段正实渲、待新片独审。新S29灯框不再挡住嘴，灯罩局部透明度已调整，小火苗和鼓腮表情可读；这一帧许可不等于整段通过。S14奶奶搭床单图、S31手电开镜时序继续推进。

64ad53a只绑定S07/S13，S29尚未绑定；后续02cb28a已保存最终audio/build.py修订，[远端读回](remote_readback/02cb28a.json)字节一致。S30新尾待下个实现提交。恢复后请以具体提交/源hash和实际片互审，不以模块数等同动作完成量。S20腕镯仍保留已有两条臂链证据，未擅自整体翻回镜头。

原始作者/独审报告的 `/tmp` 路径属于审查现场记录；可发布的视频链接已改为本仓库路径。所有解码帧不重复上传，但全帧联系表、原像素问题帧、固定MP4、逐帧hash保留；目录README给出解码方式。
