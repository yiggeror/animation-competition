# S13 Astra 接入候选：实渲自检

结论：已交可供主审保存/试接的 **5 秒、960×540、24 fps 实际候选**。A 凝视右侧鹤约一秒，短停后切为转离鹤的 B，再完成局部哈欠开合。白领、双肩和胸部保持 A；最终原帧中，已修掉颈根双线、发丝灰白残边及闭口时的嘴上透明孔。转向是明确的两姿切换，不能称连续三维转头。

## 实际交付与版本

- 视频：`s13_astra_local_24fps.mp4`，SHA256 `025b7e929eb356043c2703204691cc462bdab5d121b245ab4e5b40f2cc03e307`。FFprobe/FFmpeg 实查：H.264，960×540，24/1 fps，120 帧，5.000 秒，无音轨，全片解码无错。
- 原帧：`frames/00000.png` 至 `00119.png`；逐帧 SHA256 在 `frames/manifest.json` 与总 `manifest.json`。快速证据：`contact.jpg`、`turn-contact.jpg`、`mouth-contact.jpg`。
- 工作树 `/workspace/animation-competition-astra`，分支 `codex/astra-integration-20261017`。渲染启动基底 `bb9cd1c1458aeae93edd7562783c6643864a540f`；期间 root 合并/提交到 `e90e9cd1ff87e47b550d2cf837e6d9e736ca8623`。实际 S13、四层资产及录入的 renderer/crane/背景等依赖哈希前后一致；不以变化中的 HEAD 单独指认本片。
- 本代理只新增 `js/paint/shots/s13.js`、`tools/cutout_s13.py` 和 `assets/chars/x13_{body_a,head_a,head_b,mouth_b}.png`。没有修改 EDL/audio/其他 shots/global renderer，没有 commit/push；后续保存由 root 协调。
- 源码 SHA256：`e2a8f997d5d6318dab62c3c6dce6116a65d675dd8f861a6ccbbb99f39643d5dc`；helper：`da89d72c8ae9a9542fa72aa9e172d21772885cf09ff0b4f2ffd55bb4994b76ca`。

## 素材与接层

原件 A SHA256 `d4acbf61628b31f0d4d93768733ae8bb79b73a8a09334fac452aea4e84390696`；B `e01f440740e360564214014df7a983745cbf153d66675b55fd7c74343205c09e`，均已获独立静图有限采用。最初从 `/tmp/laidian-produce-s13-stare/` 与 `...-yawn/` 接入；root 随后发布的 canonical `collab/refs/anim_13_xiaoman_stare.png` / `anim_13_xiaoman_yawn.png` 与原件同哈希。

B 不是原坐标互切：按领口锚右移 1、下移 29 源图像素，只提取头颈和双辫；A 白领、肩胸始终是前景固定层。A 下颈根作短空间羽化的固定接缝底层，覆盖 B 自带的衣领黑线；没有整幅溶解或长网格脸部变形。头部只作围绕颈根的小幅刚性起落，峰值姿态由原始 B 提供。

哈欠用 B 原口形切片做局部纵向开合（比例 0.18–1），原口形背后是同一 B 的邻近面颊像素补片；没有新画嘴唇、牙齿或新增手。源头抠图显式保护眼白与口内白牙，清理外轮廓中性灰；羽化边 RGB 取相邻前景色，避免带灰底的透明像素在暗部发亮。A/B 原件未修改。

已实际从 canonical 用以下命令在 `/tmp` 重跑，四层输出均与当前资产逐字节一致：

```bash
python3 tools/cutout_s13.py \
  collab/refs/anim_13_xiaoman_stare.png \
  collab/refs/anim_13_xiaoman_yawn.png \
  --out /tmp/laidian-integration-s13/repro-assets \
  --report-dir /tmp/laidian-integration-s13/repro
```

## 时序、构图与实际检查

`state.json` 保存全部 120 个采样。0–1 秒保持好奇凝视；1–1.2 秒短停/轻微起势；1.2–1.55 秒是两姿切换的起落区间，**实际 A→B 发生 F32→F33，即 1.3333→1.375 秒**。这一区间的存在不等于拥有连续转头中间姿。B 嘴随后张开，2.25 秒到峰值，3.05–4.25 秒收口，最后短停。

实际看过全景关键帧、F28–39 连续头颈原帧和 12 个哈欠开合裁片。最终未见 A 旧头/双辫残影、重复肩线或嘴上小孔；领口保持原 A 轮廓，口形开合未牵动鼻眼与脸轮廓。独审另由 `/root/puppet_audit` 对同一视频哈希执行，作者自检不代替其结论。

构图使用 S12 同一墙面来源、樟木箱/蓝布色彩和同 `makeCrane(1.35,'plain')` 的虚焦前景。反向近景设计将马灯布在画右前方；A 的右上视线指向右侧鹤，B 明确转离。面部仅叠很弱的红绿透光色，全部暖光在程序中加入，没有白灰底，也未重复生图。此处是同场景近景设计，不宣称已完成精确三维灯位/轴线测量。

人物定位固定 `{x:330,y:-30,scale:0.85}`。源图 y1465 下截边映射为镜头坐标 y1215.25，低于 1080 镜框 135.25 像素，即 960×540 输出下方约 67.63 像素。实际原帧确认下截边未入画，头顶翘发与双辫保留。

只读核对 `audio/build.py`：直接关联 S13 的是火苗响度曲线（当前 155 行）；S12 扬琴在 4.6/5.0 秒，布/皮革声在 S12 1.5/2.4 秒，没有独立 S13 哈欠或转头 sfx cue。因此没有自行加喘息或改音乐。本片无声，未冒称正常速度音画试听通过。

## 剩余边界

本近景用一拍停顿和立即转避表达「发现奶奶看她」，没有奶奶反打或独立眼球移视素材；该心理含义仍需主审结合 S12 接片判断。没有制作全身退回/坐好。哈欠是局部口形开合而非完整下颌骨表演；转头是两姿切换，节奏是否接受由主审决定。最终证据只对应本报告视频哈希，早期 `keys-v1/v2/v3` 和 `frames-v2-interrupted` 均不是最终交付。
