# S07 实片、手机24fps、S13表演图与最终音轨重建

2026-10-17 06:24 UTC。原协作分支仍只提交本方collab资料；独立实现分支为 `codex/astra-integration-20261017`。Opus最新实现仍是09e423d，本方上次素材提交3d8a00d已完成[远端字节读回](previous_delivery_remote_readback.json)。不等待Opus限额恢复，按用户授权继续制作与互审。

## 可直接看的实际视频

- [S02 手机游戏，24fps带声](phone_actual24/S02_24fps_audio.mp4) 与 [S05 手机没电，24fps带声](phone_actual24/S05_24fps_audio.mp4)：本轮用当前原渲染器实渲各96帧，960×540，手机实现与3d8a00d一致。不是把旧12fps片补帧；[指根实际帧](phone_actual24/s05_root_seams_actual.png)保留F29/33/69/74/84/85/86/93。主审实看旧裂缝未回归，整段独立复审正在收口，不能称未审的每帧均通过。
- [S07 扇风、摸马灯，24fps带声](s07/S07_24fps_audio.mp4)：5秒120帧。[独立报告](s07/independent/report.md)逐帧核活动臂/手灯接触，无本次范围内结构硬伤；[作者范围](s07/report.md)、[来源哈希](s07/render_manifest.json)。源码已在独立分支提交bb9cd1c，未合并到Opus分支。
- [S07→S08 连续11秒联片](s07/S07-S08_contact_review_24fps.mp4)：两镜均为本轮24fps实渲，从同版母带连续42–53秒配音；[主审补充](s07/MAIN_CONTACT_REVIEW.md)。剪辑省略完整翻身、步行、闭握取灯及放台面，未伪称连续全套动作。
- [S30先关电视版，静音中间候选](s30_review/s30_tvfirst_silent.mp4)：12秒288帧；[原手段独审](s30_review/independent/report-original.md)与[TV先关补审](s30_review/independent/report-tvfirst-addendum.md)。手绳接触、F144灭灯、F147放手可采用。尾部4秒空绳偏长已接受反馈，正接新的奶奶大头影；此文件不冒充即将完成的新尾版。

[带声短片封装命令/原音轨hash/实际ffprobe与测量](muxed_clip_manifest.json)。这些声音实际存在，但没有主观试听，不能把文件有声写成听感通过。

## 三张新原件已独审

| 原件 | 尺寸 | 静态结论与记录 |
| --- | --- | --- |
| [S13好奇凝视A](../../refs/anim_13_xiaoman_stare.png) | 1024×1536 | [作者](s13_stare/author/README.md) / [独审](s13_stare/independent/report.md)：头颈身份成立，胸像下截边保持镜框外。 |
| [S13扭头假哈欠B](../../refs/anim_13_xiaoman_yawn.png) | 1024×1536 | [作者](s13_yawn/author/README.md) / [独审](s13_yawn/independent/report.md)：只接B头颈双辫，A身体白领固定；B肩领上移29–31px且有重绘，不整图切。 |
| [奶奶鼓腮准备吹灯](../../refs/anim_29_grandma_prepare_blow.png) | 1024×1536 | [作者](grandma_blow/author/README.md) / [独审](grandma_blow/independent/report.md)：限完整头颈近景与头影来源；右肩被裁，须镜外；不能报告完整双肩胸像通过。 |

全部为内置image_gen原件字节相同副本，未放大。A/奶奶各单次生成，B单次限定编辑，无重试。实际prompt/request/hash和偏差实测完整随附；不冒称底层模型。鼓腮图只有准备姿态，实际马灯持续点亮、嘴影可读性与真实灯-头-布投影仍在接入，尚未动态通过。

## 当前可复现的真实音轨

[归一化WAV](audio_final/film_mix_norm.wav) 与 [全片256k AAC](audio_final/FULL.m4a) 来自独立实现工作树新源码，**不是Opus新交母带**。245.5秒，包含244.5秒EDL和末尾1秒低电平尾响缓冲。

- 当前WAV：**-16.04 LUFS / -4.40 dBTP**，SHA256 `101d818f324f55c85c793c19b42bd774d6a8393ae67ec0565260b001bb91091e`。
- 当前全片AAC：**-16.08 LUFS / -3.72 dBTP**，SHA256 `201820c3c49ad3e240cf0b4078f55a435833566562238c3905d98debeea3aa5c`。
- 31个EDL镜头各自独立编码256k，最高真峰 **-3.16 dBTP**；本批目标为最终AAC≤-1.5dBTP。不是让每个短镜都单独归一到-16LUFS。[完整33项实际测量](audio_final/measurements.json)、[源码快照与hash](audio_final/source_manifest.json)、[构建日志](audio_final/build.log)。

相对3d8中的历史候选，PCM归一TP目标最后选-4.5：-3.5目标虽整轨通过，独立S08短片仍测到-.79，不能外推。保留历史文件便于核对，新母带优先用本目录。另按script-v3修两项时序：S30先在1.1秒关电视（画面CRT熄灭、声门/开关同刻），1.5秒脚步接走向门边，6秒只关日光灯；吊扇在关灯后继续转，不再随日光灯停。没有改旋律、重配音乐或降低响度目标。

音轨的新源码只存在本目录快照和独立代码分支，原协作分支audio代码未覆盖。独立声音审查前一版的参数实验报告只覆盖其固定文件；本批的实际测量明确对应本批hash。任何后续剪辑/重编码还要测最终输出，数字检查不替代主观试听。

## 当前仍在推进

S13五秒实际近景、S29末准备吹灯、S30尾大头影正在接入及实渲；最终代码和新片另批发布，不提前说完成。S14虽有mod，人物搭台仍未补；S28双人眯眼、S29折鹤颈/逐件收偶等仍需补实际表演。旧249秒粗剪没有被本批偷偷更新，也不是正式成片。
