# 新骨架引擎：接入前阻断与可运行复现

[独立完整报告](report.md)。固定66ea5f7的warp.js，SHA256 `56848d3801ab8c468549c84683e0bb3e2ececd8d5af8db7de4197fc80984805c`；本包只是审查、复现脚本与建议，没有修改Opus引擎。

1. **跨尺寸A→B→A使第三次A全透明。** 实际Chromium/WebGL2报1282，VAO属于旧context；不透明像素1536→0。重新bind对照恢复且与第一次PNG一致。[实际图](66ea5f7/evidence/context_comparison.png)。建议稳定复用同一GL上下文并调整画布尺寸，或资源完整按context归属缓存；修后跑同一复现。
2. **keepUnder保像素却缺网格。** body纹理探针仍不透明，子层移开后输出透明洞；body的inLayer始终排除该区域。[实际图](66ea5f7/evidence/keep_under_comparison.png)。网格与纹理须采用同一纳入规则；仍不能将保留旧手臂像素等同补出隐藏躯干。
3. **body内新pin已验证有效，旧“全部未读”关闭。** 但独立arm层不允许root时，默认root pin被过滤掉，静默回退arm，实算漂移1.9967px。[另一位独审的bind/矩阵复现](pin_layer/consumer_reproduction.json)，不混称WebGL像素实验。

这些都是小合成图的真实引擎路径检查，未调用图像生成，未启动全片渲染，不冒称人物自然表演验收。S01小满数据继续，奶奶现成6秒片独审继续。
