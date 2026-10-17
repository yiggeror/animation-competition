# S18 法线单变量修复证据（小交付包）

结论：母版 `x18_laugh_n.png` 精确匹配默认 `card_maps.py` 分块法线；新 v1/v2 经 `card_soft.py`，因此切回母版时面颊、领口、裙面和发缘凸起亮边骤增。仅替换母版法线的 F21 真实渲染，已显著减轻跳变。

**落地建议：为 S18 的复用母版建立专用卡/法线，采用与新卡一致的 card_soft，再把本镜头 manifest 指向该专用素材；保持全局共享 x18_laugh_n.png 不变。若保留 x16 开头，也在 S18 专用副本中统一检查法线，避免影响其他镜头。**

文件：
- `report.md`：完整 ded37ed 增量报告的原样副本；其中其他审查附件位于原 `/tmp/laidian-s18-pilot-audit/compositor_ded37ed/`，本小包不重复收录。
- `normal_control_comparison.png`：F18 当前、F21 当前、F21 只替换母版法线三列。
- `normal_cause_probe.json`：全图 Alpha>240 区域、向量归一化后的倾角统计、默认 card_maps 重算与现有母版逐像素一致的结果。
- `master_soft_control.png`：实际单变量替换的法线，635×1175；没有更改 albedo/材质/灯光/位置。
- `baseline_render_manifest.json`、`control_render_manifest.json`：真实渲染依赖及其 SHA。二者仅 `assets/chars/x18_laugh_n.png` 的哈希不同；控制清单中该项 sourceUnchanged=false 是故意覆盖。
- `card_soft_reviewed.py`、`rerender_control.cjs`：复现所需小脚本。

复现法线（写入 /tmp，不覆盖仓库）：

```bash
python3 -I card_soft_reviewed.py /workspace/animation-competition/assets/chars/x18_laugh.png /tmp/s18_master_soft_reproduced.png
```

参数为默认 sigma45、强度0.35。预期 PNG SHA256 为 `356b4144a0e9f2ea030c32ce48e08b6afca4237d15bee9482b6e68579c838f12`。

复现控制帧：在仓库与本包清单对应的版本上运行 `node rerender_control.cjs /workspace/animation-competition`，结果写本包 `rerender/`。它只在本地HTTP响应中替换法线，绝不写仓库；依赖 Playwright 的当前环境安装路径和 `/usr/bin/chromium`。该便携脚本只改了原已执行脚本的输入/输出路径，做了 node --check，没有再次运行整帧渲染；原实际执行证据在两个 manifest 中。其他版本运行结果不能冒充已冻结版本。

这是技术单变量因果证据，不是完整动作、正常速度观感或最终美术风格的通过声明。没有视频及30帧序列。
