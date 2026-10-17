# 《来电》新母带独立重建 / S01、S04 音轨核验

**结论：当前不能认证试片绑定了所报新母带；两个关键样本更贴合“恢复旧 beans 行”的反事实重建。** 这不等于已识别到实际使用的旧文件。

- 仅在本轮沙箱的隔离副本构建，未修改生产源码、现有交付物或推仓库；未生图、未渲视频、未访问旧任务/用户电脑。源 HEAD `b6e57dc`，`audio/build.py` blob `7023d6f`，新片来自 `340b3a2`。本地 shallow clone 无 0606d3a 对象，删除行已通过 GitHub commit 与当前源代码交叉确认。无 AGENTS.md；已读 README 与 build.py 构建说明。
- 工具：Python 3.12.14 / NumPy 2.3.5 / SciPy 1.17.0 / Node 24.19.0 / FFmpeg 7.1.5；试片标记 Lavf60.16.100。新源码两次构建全部五条 WAV 文件哈希一致。

## 1. 母带与 S03
- 新母带：48 kHz、双声道、16-bit PCM，245.500 s（EDL 244.5 s + 1 s 尾音）；实测 −16.03 LUFS、−4.39 dBTP、LRA 8.3。第二遍 loudnorm 实测仍是 dynamic。
- 所报文件 SHA256 `6980b2ffd039ca4189fdac15ca71c36a7422a61a56bee9454ad8714490de9ede` 未复现。新构建为 `123fa73a9e147cdeffe0dcda58652d79dd415eff6e45e108e43a2aed0c329780`；仅模拟原编码器 ISFT 头仍不命中，不能把差异认定只是容器标签。跨工具链原因尚未定位。
- 源码 AST 与第二次实际运行轨迹均仅发现 S01 的 12 s beans 调用；S03 不再调用整镜 beans。3.8/4.0 s 两条 cue 均实际生成非零音频（母带 19.8/20.0 s）。这是源码/运行期验证，未作试听。

## 2. 实际新片音轨
- 实测 AAC LC / 48 kHz / stereo，音频时长20.021333 s，480帧视频20 s；−15.32 LUFS、−4.37 dBTP。取片段的响度与全片不同可正常发生；真峰低于 −1.5 dBTP。
- PTS 对齐后，S01 对应母带 0–12 s，S04 对应22–30 s；两镜共同的音频起点是1024采样，视频起点0.020996 s，差约+0.337 ms。早先32 ms推断已撤回：直接WAV解码忽略重叠PTS，不能据此宣布播放器音画延迟。
- 关键窗口（各0.7 s，先按PTS对齐、再搜索采样偏移并拟合增益）：
  - 母带22.1 s：新源相关0.977679 / 增益0.948373；恢复beans反事实0.998786 / 0.995402。
  - 母带22.5 s：新源相关0.981125 / 增益0.951271；反事实0.999674 / 0.996926。
- S04其余窗口对反事实增益约0.994–0.998，对新源约0.948–0.975。证据不支持直接沿用“新母带已绑定/旧PCM一致”的验收结论。

## 3. 核验身份与最小补证
PCM哈希均指去掉WAV头、48kHz双声道交错signed 16-bit little-endian字节：
- 新源 film_mix.wav 文件：`1d658b8edfc1d09bdf82c5a271b74e64e1a720a1418a103135ef9d0a916ddeab`
  PCM：`1b4c793143538a2522cd13cfbf3ed5359799314373e1335aaf4e2151c1fc8475`
- 新源 film_mix_norm.wav 文件：`123fa73a9e147cdeffe0dcda58652d79dd415eff6e45e108e43a2aed0c329780`
  PCM：`ba1cf05496dd0730570cc82c6a663bac7f0c715bcdade21bda44388def15aa8b`
- 恢复beans反事实 film_mix.wav 文件：`d75794432a81ab669bb556a61b48f3b5849ea22e087f54291b9e4b2ca866c07d`
  PCM：`292276c2ae75c30575d91d6c1c01b7447f946b202ac9d5ffb9fc851e2360cf8e`
- 恢复beans反事实 film_mix_norm.wav 文件：`6980ce06f50f6348b8f832d23cfb4a5d72edddda61ab47ade274727ecaaf18c4`
  PCM：`9dff5a4a41e39ed568b872f56b5fd5573d2f8ead6e75bdd86ce854d449cf138a`

**给 Opus 的最短请求：** 请给 S01/S04 实际 mux 输入路径与文件 SHA256，并提供所报 6980…ede 母带的可读 WAV，或其 s16le 双声道交错 PCM SHA256 + Python/NumPy/SciPy/FFmpeg 版本。当前试片样本更贴合恢复旧 beans 的反事实，需核对输入后才能认证新母带已接入。

详细可复核数据：audio_verification.json；analysis/preview_alignment_pts.json、counterfactual_preview_alignment_pts.json、runtime_cue_trace.json；logs/ 保存原始构建与测量日志。
