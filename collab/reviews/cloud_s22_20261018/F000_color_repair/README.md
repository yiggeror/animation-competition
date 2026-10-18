# S22 F000：同 raw 最小修色候选，待 Astra 锁母

- [修后透明原尺寸 PNG](candidate/F000_repaired.png)，1672×941；[2×握点修前后](qa/grip_before_after_2x.png)、[灰底全图修前后](qa/before_after_gray.jpg)、[修色域叠图](qa/color_masks_overlay.png)、[各独立 mask](masks/)。已实际打开握点对比、mask 叠图、白底和黑底检查。
- 奶奶独立肤域加色起点 `(+1,+6,+12)`，小满 `(+1,+3,+8)`；原定掌面 ROI 中位数修后分别为 `(254,210,177)` / `(254,205,171)`，与两位角色原手目标逐通道差均为 0。保留原来的渐变和阴影，暗色连续减弱修色；未平涂。
- 深线 22,827 像素及两处原图可见拇指甲 2,447 个不透明像素 RGB 未变，签子排除域 RGB 未变；两块不透明轮廓完全一致，最短空气隙仍为 19.209px。未变形、重画、移动、缩放。
- 只清掉 3,339 个与主轮廓断开的低 alpha 散块，共 22,110 像素，实际最大 alpha=1/255；主轮廓相连的全部 alpha（包括细抗锯齿）保持原值，距主 alpha 轮廓 2px 内的散点也保留。透明散块的原 RGB 未改。

[完整测量与 SHA](provenance/correction_measurements.json)；[可重放处理脚本](repair_same_raw.py)。命令：`python collab/reviews/cloud_s22_20261018/F000_color_repair/repair_same_raw.py`（Pillow/NumPy/SciPy）。

依据 Astra 授权：首图结构双审通过，只做同 raw 最小修色和不连主轮廓低 alpha 清理；0 次新调用。原 `f2b445041465ab9bed0cbf973036747c71a6f020` 的 [raw](../F000_first/originals/F000_call01_raw.png)、完整提示词、输出及来源均保全，raw SHA `57f14bae2b0e48cf35e0270f7d7384e28719897282bd1ff02b036ec429e52353`。

本修复新调用 0 次，S22 累计 1 次。仅交锁母审，未生成 F012/F024 或其他状态，未改曝光表、共享实现、音频或 ready。
