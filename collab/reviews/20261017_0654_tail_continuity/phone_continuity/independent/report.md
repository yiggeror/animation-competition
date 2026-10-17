# S04→S05 停电状态连续性：独立小项复验

**结论：本次状态栏错误已关闭，手与游戏动作未见回归。** 修后 S05 从 F0 即显示 1%、无充电闪电；不再在 S04 已断电约 7.4 秒后重复播放充电与 2% 状态。本次仅验该修复，不重审全部按压节奏。

## 绑定文件与实看

- [修后视频](../author/s05_fixed_silent.mp4)，SHA256 `4b446e21d842ac577343ed10f1abafb76f2f4e558ee3f16ecdcacc0fb52c4d19`，1,110,609 字节。
- 独立 ffprobe：960×540，H.264，24 fps，96 帧，4 秒，无音轨；见 [ffprobe.json](ffprobe.json)。
- 已实看 [旧联剪联系表](../author/old_join_contact.jpg) 与修后联系表；另从修后 MP4 独立解码 F0–12，制作 [前12帧状态栏原像素序列](evidence/final_decoded_first12_status_native.png)，并查看 [修后首帧全景](evidence/fixed_f0000_full.png)。

旧联系表中 S04 F14（0.583秒）尚亮、F15（0.625秒）已进入断电状态，与源码 T_CUT=0.6 秒相容。S05 在总片 30 秒开镜，旧 F0–5 仍显示闪电，旧 F0–11 仍为 2%；这是已发生断电之后重复交代旧状态。

修后解码 F0–11 全部为 1%、无闪电。F0–7 红色低电警示、F8–11 白色是既有低电闪烁，未读到充电恢复；[F12 全景](evidence/fixed_f0012_full.png) 接续相同 1% 状态。未见数字覆盖手指或新增 UI 错位。

## 独立回归证据

已独立逐帧读取旧 PNG 与修后 PNG，比对 96 条帧 manifest 哈希，全部相符。F0–11 的所有像素变化都位于状态栏矩形 `(405,185)–(630,285)` 内，框外逐像素相同；实际差异 bbox 与原 manifest 相同（manifest 的右下角使用包含末像素的坐标约定）。**F12–95 共84张图与旧原帧逐字节相同。** 见 [独立像素及哈希核验](independent_verification.json)。这直接支持手、手机、游戏与镜头没有因本修订改变。

另在 Node 中只调用两版 `state(t)`，对 96 个 24fps 时刻独立重算：去掉 `status` 后全部相同；F12 起完整 state 相同。见 [独立 state 回归](independent_state_regression.json)，不是只转述 root 提供的布尔结果。

本审运行时旧模块为 `/workspace/animation-competition/js/code/s05.js`，SHA256 `eddc2aa357033e498515e8af84ebcfb83c76008fa73989c22439c611041c52e7`；修后模块为 `/workspace/animation-competition-astra/js/code/s05.js`，SHA256 `eb87b3031c31e5207ea471bd572e6160136cbb99d84241a8f0e9eb62b250e712`。源码确认开镜 `bolt=0`、`level=1`，低电闪烁随之生效。

可以合入这一小项修复。本报告不重新宣布所有按压动作、S04全部表演或音画联剪通过；修后文件无声音，也不是整段 S04→S05 的新合并导出。未改源码、未启动渲染，仅解码、比较、写证据与报告。
