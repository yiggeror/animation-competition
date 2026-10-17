# 《来电》独立音频技术复核

固定版本：`e79d4a15736cd538a0e2eaf0eb0094360392f26f`，分支 `claude/intelligent-euler-t2so6e`。审查日期：2026-10-17 UTC。仓库快照 `/tmp/laidian-review-snapshot`；所有本次输出仅写入 `/tmp/laidian-audit-audio`。

**结论：火苗时基、music 的 0.9 权重和电子声隔直均已在当前源码落实；最终 −16.0 LUFS / −1.5 dBTP WAV 尚未实际交付，不能据此放行成品。另有一项当前残留：仅总混音经过最终 15 Hz 高通，导出的三条 stem 未经过该处理，所以“相加就是总混音”仍不成立。这是新的处理链差异，不是继续漏乘 0.9。**

本轮实际读取了 `collab/README.md`、`collab/claude.md` 末尾、`collab/partner.md` 末尾、音频源码及相关 EDL/拼片代码；未发现适用 AGENTS.md。实际测量了仓库媒体流信息、两份有声交付的响度/真峰/样点/DC，并执行了火苗包络和 S25/S26 隔离 chip 分量的局部复现。没有主观听音，没有重建全片音轨，没有逐帧渲染、启动 Blender、安装包、改仓库或对外发言。

## 1. 04:09 声明逐项核对

声明位于 `collab/claude.md:594–598`；标题写 04:22，但同文件 `:613` 更正为实际 04:09。以下全部按当前固定源码判断。

| 声明 | 当前证据 | 可关闭到哪一层 |
|---|---|---|
| 火苗时基已修 | `audio/build.py:152–156` 先生成全片 `gain_curve`，再截取从 `s0=ns(LAMP)` 开始的窗口；不再将绝对 cue 直接解释为局部时间 | **源码/局部计算通过**；尚未从新版成品复验 |
| music stem 已乘 0.9 | `audio/build.py:541` 先执行 `music = music * 0.9`，`:542` 和 `:546–547` 同用此 music | **原权重缺失关闭**；“三 stem 相加等于 mix”另有下述残留 |
| 电子声隔直，DC 约 1e−5 | `audio/build.py:533–534` 给 chip/beat 做 20 Hz 高通；`:543` 给总混音左右声道各做 15 Hz 高通；滤波定义 `audio/inst.py:42–43` | **隔直确实实现，局部 chip 计算有效**；1e−5 的整片/时窗/声道口径及新版成品数值仍是作者自报 |
| 两遍 loudnorm 后 −16.0 LUFS / −1.5 dBTP | `audio/build.py:549–554` 实现两遍流程，目标参数符合声明；`:555` 打印的是目标，不是输出后的第三次实测结果 | **配置核对通过**；无该 WAV，不能独立复测声明 |

火苗局部复现直接调用从当前 AST 提取的 `gain_curve`，保持 48 kHz 时基；当前 EDL 下结果如下。这里是**增益包络 dB**，不是听感响度，也不是成品测量。

| 全片时刻 | 事件/控制点 | 本次复现 |
|---:|---|---:|
| 48.8 s | S08+1.8，火苗起点 | −18.3451 dB |
| 51.0 s | S08+4，近景 | −18.0000 dB |
| 53.0 s | S09 起点 | −28.0000 dB |
| 170.5 s | S27 来电 | −40.0000 dB |
| 202.5 s | S30+7，恢复点 | −28.0000 dB |

旧的额外 +48.8 s 位移已不再出现在当前计算；不得继续把它列为当前未修。

隔直局部复现执行的是当前 `build.py:365–462` 的 S25/S26 排程，省去无关合成，将 S25 时间原点移到零；只测 **声像/混响/总混音前的 chip 分量**：

| 窗口 | 高通前样点均值 | 20 Hz 高通后均值 |
|---|---:|---:|
| S25，6 s | −0.03871738 | −1.65e−8 |
| S26，18 s | −0.02528780 | +6.73e−7 |

这些数值支持隔直措施有效，不能替代最终 master 或其 AAC 的 DC 实测，也不能拿来核准作者未明确口径的“约 1e−5”。本轮进度消息曾误说 25 Hz；正式核对为 **chip/beat 20 Hz、mix 15 Hz**。

## 2. 当前须修或明确：stem 与 master 处理链不一致

`audio/build.py:541–548` 的实际顺序：

1. `music *= 0.9`。
2. `mix = music + SFX_r + AMB`。
3. 只给 `mix` 做每声道 15 Hz 高通，并从过滤后的 mix 取得统一峰值缩放。
4. 三条 stem 则直接从过滤前的 `music`、`SFX_r`、`AMB` 乘同一缩放、量化写出。

因此，量化前 `sum(stems) = scale × (music + SFX_r + AMB)`，而 `film_mix = scale × HP15(music + SFX_r + AMB)`。这已与之前的“music 少乘 0.9”不同。即使统一权重，该滤波器仍不等于恒等运算；独立 16-bit 量化还会带来较小的求和差异。

本轮用真实 S25/S26 chip 合成分量、相同 20 Hz→声像/权重→仅 master 15 Hz 的局部路径验证：导出的 stem 形式与 master 形式有非零差异，差值 RMS 约 −28.84 dBFS，最大绝对差 0.23029 FS，且没有分轨削波。**这是隔离分量的工程探针，使用局部自身峰值归一；不是三条真实全片 stem 的误差或可闻性测量。** 足以证实“仅总线高通”破坏直接相加等价，不能据此推断整片误差大小。

建议明确交付约定：若要求相加复原 `film_mix.wav`，分轨与总混音应共享同一高通和增益链，再在容许量化误差内验收；若提供的是 master 处理前的重混分轨，就标注处理阶段并撤回“相加就是总混音”。归一化后的 `film_mix_norm.wav` 另有 loudnorm 处理，更不能直接用当前三个 stem 的等增益求和替代。

## 3. 实际交付文件与本次复测

全仓媒体清单共 23 项；只有以下两项含音轨，均为 48 kHz 双声道 AAC。**新回交 S15/S17/S18/S20/S22/S25/S27 短片均无音轨**，不能用来复验新版声音。仓库没有 `film_mix.wav`、`film_mix_norm.wav` 或三条 stem；`.gitignore:3,6` 明确忽略 build，这是交付位置选择，不是修正失败的证据。

| 实际文件 | 时长 | 本次输入响度 | 本次输入真峰 |
|---|---:|---:|---:|
| `renders/checkpoint2/film_preview_v1.mp4` | 容器 249.000 s；解码音频 248.981333 s | −21.72 LUFS | −0.41 dBTP |
| `renders/checkpoint2/music_theme_demo_v1.m4a` | 容器/音轨标称 30.000 s；直接解码 30.016 s（含 AAC 尾部样点） | −15.81 LUFS | −0.99 dBTP |

使用本机 FFmpeg 7.1.5，读取 loudnorm 测量 JSON 的 **`input_i` / `input_tp`**；日志里的 `output_*` 是滤镜试算输出，不是已交付的新 master。本次没有保存或冒称生成新的归一化成品。两份原件解码后均无样点达到或超过满幅。

全片 SHA-256：`51e5b1d93c83b2ea484973ba9030f2f5dc6728e8a8ea28e6141fa8c2bbba51af`，与 `collab/reviews/20261016_1639/full_cut_review/independent_full_cut_5b2504f_review.md:29` 中的固定 `5b2504f` 旧片完全一致。**它不是这次音频修订的成品。** 本次旧片 S25 [144,150) 与 S26 [150,168) 左声道 DC 分别复测为 −0.02777430 / −0.01940333，与旧报告吻合；这些数字不能指责 e79d4a1 的隔直修正无效，也不能验证新版修正已进片。

主题小样 SHA-256：`206595c5e17c9ae1b693dc5661366bfeacccf22b3843a3bf41fce5ed1810b273`。其 [18.5,22.5) 左声道 DC 本次为 −0.10434071。`audio/demo.py:67–73` 仍有独立的小样混音路径，未继承 build 的新隔直；该旧示范文件同样不能代表新版全片 master。

## 4. 当前版本时基与下一份交付

当前 `js/film/edl.js:34` 已新增 2.5 s 的 S24，`:48` 的 END 是 9 s。独立读取 EDL 得到 **245.5 s** 全片长度；`audio/build.py:33` 再预留 1 s，预计合成缓冲 **246.5 s**。当前 S25/S26/S27 起点分别为 **146.5 / 152.5 / 170.5 s**，与旧全片的 144 / 150 / 168 s 不同。

04:09 声明的下一步仍是“新增 S24”（`collab/claude.md:600–601`），且未附音频生成时的 commit、EDL 或 hash；所以不能默认它的 −16.0 / −1.5 测量已经涵盖固定快照的新时长。

下一轮只需补齐以下证据，无需为了本次审查重渲全片：

- 可访问的、注明生成 commit/EDL 和 SHA-256 的新版 `film_mix_norm.wav`，或实际采用它的有声预览；不用强行将 build 纳入 Git。
- 若继续承诺分轨可相加复原，补相同版本的 `film_mix.wav` 和三条 stem，按约定处理阶段测求和差异。
- 对真实输出重新测整体 LUFS/真峰及 S25/S26 的每声道 DC，保留实际测量日志；最终 AAC 编码后再核真峰。
- `tools/film.mjs:37` 仅在显式 `--audio` 路径存在时混音，`:2` 示例仍是 `film_mix.wav`；新版正式拼片须明确选中 `film_mix_norm.wav`。该工具会用 `-shortest` 截短，因此音频缓冲多出的 1 s 不会自然延长画面，片尾需要按最终裁切长度复核。
- 实际试听仍未完成。音乐平衡、音色、切断处听感和尾声都未获本轮听审放行。

## 5. 支持材料

同目录下已生成：

- `media_inventory.json`：全部 23 个实际媒体的 hash、时长和流信息。
- `film_preview_v1_loudnorm_measurement.log`、`music_theme_demo_v1_loudnorm_measurement.log`：本次对原交付文件的 FFmpeg 实测原始输出。
- `delivered_audio_sample_metrics.json`：本次解码样点、DC、RMS、峰值及检查时窗。
- `focused_checks.py`、`focused_checks.json`：源码局部复现方法与结果，可运行 `PYTHONDONTWRITEBYTECODE=1 python3 focused_checks.py /path/to/fixed/snapshot`；只读源码，结果写入本审查输出目录。

未建立整片新合成与作者 WAV 的逐样点同一性；未声称已听音。快照 `git status --short` 在审查后为空。
