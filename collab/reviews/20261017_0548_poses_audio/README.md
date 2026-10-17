# S29/S30 新姿态与实际音频重建（云端 Codex）

2026-10-17 05:58 UTC 整理；最后核到 Opus 远端 `09e423da80f687ce176db856e612ba2c558621d2`。用户告知 Opus 限额，并明确授权独立制作、整合和实际画面/音频检查。我们不把暂时无回复当遗漏；实现只在独立 `codex/astra-integration-20261017` 分支推进，原协作分支本批仍只增加 collab 素材及审查记录。

## 可接入的静态素材

| 素材 | 实际原生尺寸 | 作者记录 / 独立审查 | 通过范围 |
| --- | --- | --- | --- |
| [S29 奶奶包布](../../refs/anim_29_grandma_wrap.png) | 1024×1536 | [作者](s29_grandma/author/README.md) / [独审](s29_grandma/independent/report.md) | 两手扶折布瓣、膝面承托、近右裸腕及远左绿镯成立；只覆盖包裹将收口终段。 |
| [S29 小满 A](../../refs/anim_29_xiaoman_phone_look_a.png) | 1024×1536 | [作者](s29_xiaoman_a/author/README.md) / [独审](s29_xiaoman_a/independent/report.md) | 看席上手机、左手留短签、右掌轻撑；尚待真实手机目光落点和乌龟接杆。 |
| [S29 小满 B](../../refs/anim_29_xiaoman_phone_look_b.png) | 1024×1536 | [作者](s29_xiaoman_b/author/README.md) / [独审](s29_xiaoman_b/independent/report.md) | 抬头转看可读；只接B头部/必要颈，保留A白领与全身。 |
| [S30 拉绳 v2](../../refs/anim_30_xiaoman_pull_cord.png) | 1024×1536 | [作者](s30_v2/author_review.md) / [独审](s30_v2/independent_review.md) | 薄底凉鞋、提踵与前掌承重已成立；手握单绳姿态可试接，不等于拉绳动画通过。 |

这些 canonical 都是内置 `image_gen.imagegen` 原件的字节相同副本，没有放大、重画或伪称底层模型。实际 prompt/request、原件 hash、作者自检和独审均随目录保存。奶奶、S29 A 各单次生成；S30 首稿鞋底误成楔形厚底，被主审和独审拒用，v2 仅一次针对鞋踝的限定编辑。旧 [S30 首稿记录](s30_v1_not_adopted/author_review.md) 保留，不采用为 canonical。v2 非目标区有细微像素变化，不能声称逐像素不变。

S29 按 `docs/preproduction/script-v3.md` 第11场保留“手机在竹席上、手里仍攥乌龟签”。这与 Opus 原清单的“拿着手机”不同，明确记录，没有悄悄增加捡起手机的动作。S29 A 是新的剧情姿态，不是之前拒绝的低凳双手置膝或托腮方案重试。B 抬头图已完成主审与独审，可有限采用头部；实际非目标区包括领口、手和杆均有漂移，不能整张互切。

## 实际音频文件与结果

本批音频是云端按 `916257deb98240098be09d64cc7b45578e0ef8ee` 的字节一致源码快照自行重建，**不是 Opus 新交母带，也没有进行主观试听**。[源码/输入清单](audio_rebuild/source_manifest.json)、[构建日志](audio_rebuild/build.log)、[原归一链测量](audio_rebuild/verification/measurements.json) 和 [4倍采样峰值定位](audio_rebuild/verification/peak_localization.json) 可核。

| 实际文件 | 综合响度 | 真峰 | 结论 |
| --- | --- | --- | --- |
| [原 -2.5 目标重建 WAV](audio_rebuild/film_mix_norm.wav) | -15.96 LUFS | -2.40 dBTP | 245.5秒、48kHz双声道，含当前244.5秒EDL之外1秒缓冲。 |
| [对应 256k 全片 AAC](audio_rebuild/verification/film_mix_norm_256k.m4a) | -15.99 LUFS | -0.66 dBTP | 没有满幅越界，但55.902秒附近编码后峰值高于所需余量；不能只测S28就宣称全片通过。 |
| [新 -3.5 目标候选 WAV](audio_rebuild/ceiling_candidate/film_mix_norm_tp3p5.wav) | -15.96 LUFS | -3.40 dBTP | 同一原始混音，只改变两遍 loudnorm 的 TP 目标。 |
| [对应新 256k 全片 AAC](audio_rebuild/ceiling_candidate/film_mix_norm_tp3p5_256k.m4a) | -15.99 LUFS | -2.05 dBTP | 本文件达到最终 AAC ≤-1.5dBTP 的目标；整轨独立复核与各切段重编码复测继续。 |

新候选的 [实际命令](audio_rebuild/ceiling_candidate/commands.json)、[哈希/测量](audio_rebuild/ceiling_candidate/manifest.json)、[WAV原日志](audio_rebuild/ceiling_candidate/film_mix_norm_tp3p5.wav.log)、[AAC原日志](audio_rebuild/ceiling_candidate/film_mix_norm_tp3p5_256k.m4a.log) 随附。独立实现分支会记录该参数变更，原协作分支代码未改。

S28 对应174.5–182.5秒的 [PCM切段](audio_rebuild/verification/s28_from_local_norm.wav)、[160k AAC](audio_rebuild/verification/s28_160k.m4a)、[256k AAC](audio_rebuild/verification/s28_256k.m4a) 实测真峰分别 -2.50/-2.46/-2.42dBTP。这批已未复现1a90旧实交S28的+2.62dBTP，关闭该问题仅到“当前重建的这些文件”。160k与256k在新源下都通过，不能倒推旧超峰完全由码率引起。

所有以上数字来自 loudnorm 的 **input** 测量，不把测试过滤器的 output 目标当文件实际结果。响度与真峰数值不替代音色、节奏、声画和主观试听。

## 接入及余项

S07/S29/S30 各自负责者正在独立工作树试接、实际渲染并准备复审。最新09e423d有31镜244.5秒，S07/S13/S29共22秒仍无mod；S14已有临时布景模块，但缺人物搭台过程。已有模块数量不能充当镜头完成数量。S13近景表演补图已继续启动，不等待Opus恢复。

当前仍需实审或补齐的动作包括 S07取灯的过程省略是否可读、S29折鹤颈与随后准备吹灯、S30脚地/手绳/灭灯节拍，以及S14人物搭台。S20腕别具体臂链保留待双方恢复互审；不因这个争议阻塞其他镜头。旧全片未更新，本批不称正式成片。
