# 隔离试渲路径

本提交所有新增文件只在 collab/reviews，本次不改 assets/chars、assets/flips、js、audio。

`probe/` 是完整自包含资产覆盖包：
- probe/assets/chars/g03_watermelon_k*.png：11态33张三图，含已有9态的相同字节副本及k14/k15六张新图。
- probe/assets/flips/g03_watermelon.flip.json：144帧风险标记试验表。
- originals/g03_watermelon_k14.png 和 k15.png：未修改生成原件。

Opus可在自己的隔离试渲工作副本内，把 probe/assets/chars 的33张图复制到对应 assets/chars，将 probe/assets/flips/g03_watermelon.flip.json复制到对应 assets/flips；先运行 python3 -I tools/flip_manifest.py g03_watermelon 144，再渲实际S03短片回审。是否正式接入由双方看实际片决定；本包不自动执行复制或启用。k14原“中点用途失败”记录保留，本次仅改作刚离嘴闭口态。
