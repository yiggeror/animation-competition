# warp.js 引擎最小浏览器实证：66ea5f7

**最新结论：跨尺寸缓存 VAO 导致空白输出，属于接入前须修的阻断；`keepUnder` 只保留纹理、未保留底层网格的缺口也已实证。旧版“pins 完全未实现”已关闭，body 上的新 pin 语义实测有效；独立层排除 root 时的 pin 仍有缺口，见末节另位审查者的复现，不宣称 pins 全部通过。**

## 固定版本与复现环境

- 最新被测源码：提交 `66ea5f7` 的 `js/rig/warp.js`，冻结副本 [source/warp.js](66ea5f7/source/warp.js)。SHA256 `56848d3801ab8c468549c84683e0bb3e2ececd8d5af8db7de4197fc80984805c`。
- 复测时主仓 HEAD 为 `90f8a45ce7b2c098d404d1a2f1c523f4831eb341`，其中 `warp.js` 与上述文件哈希相同。行号以下均指冻结副本。
- 实际 Chromium `154.0.8037.57`，WebGL 2 / ANGLE SwiftShader。使用小型合成透明 canvas；没有修改人物图、仓库、原引擎，也没有批量渲染。
- [可运行复现脚本](66ea5f7/reproduce.cjs)、[实际结果/GL 错误/像素统计](66ea5f7/results.json)、[本次控制台输出](66ea5f7/run.log)。命令：`node /tmp/laidian-rig-engine-audit/66ea5f7/reproduce.cjs`。脚本自开临时本地 HTTP 服务并在结束时关闭浏览器和服务。

## 1. 阻断：A→B→A 跨尺寸渲染使 A 全透明

同一个模块实例，创建两个一骨绑定：A 为 96×64，B 为 64×96。骨骼使用 identity pose。依次 `render(A,{})`、`render(B,{})`、再次 `render(A,{})`，第三次沿用第一次的绑定对象，没有改动图像或姿势。

| 调用 | 实际 GL 上下文编号 | 不透明像素数 | getError |
|---|---:|---:|---|
| A 首次 | 2 | 1536 | 无 |
| B | 3 | 1536 | 无 |
| A 再次，同一绑定 | 4 | **0，整张全透明** | **1282 / 0x502 两次** |
| A 重新 bind 的对照 | 4 | 1536 | 无 |
| 上述新绑定再画一次 | 4 | 1536 | 无 |

实际浏览器控制台报：

```text
WebGL: INVALID_OPERATION: bindVertexArray: object does not belong to this context
GL_INVALID_OPERATION: glDrawElements: Must have element array buffer bound.
```

fresh bind 对照与首次 A 的输出 PNG **SHA256 完全相同**，均为 `baf41cd4af37ae76f590f4e091cbc5b1d959fa2b4943182d9c0dff40be7b288b`；第三次坏 A 是 `d1ff024747f62d26876177dab1a88c93c81e154c6459c3718b2c7475f34fa4bd`。不是人物素材、骨权重或姿势造成的差异。[对照图](66ea5f7/evidence/context_comparison.png) 的棋盘代表透明；原始透明 PNG 同目录保留。

**源码根因：** `glCtx` 第 133–140 行仅缓存一个 `GLC`；尺寸不同时第 136 行创建新 `OffscreenCanvas` 和新 GL。第 172–178 行把 `vao` 直接缓存于 `L.vao`，第 179–180 行把旧上下文的 VAO 交给新 GL。`loadRig` 又会保留绑定对象，正常跨角色反复渲染会触发该路径。

**最小修法建议，尚未代改或验证修复：** 保持同一 WebGL 上下文，尺寸变化时调整其画布尺寸及 `W/H`，继续正确更新 viewport/uniform；或让 GL 与其 VAO/缓冲/纹理资源按上下文成套持久缓存。无论选哪种，都不能让裸 `L.vao` 跨上下文复用。修后应复跑完全相同的 A→B→A 测试，第三次必须无 GL 错误且与首次 A 像素一致。逐帧重新 bind 虽能绕过本次故障，不是建议的正式缓存方案。

## 2. 缺口：keepUnder 保住 body.tex，却没有底层几何可画

使用 128×128 合成图，蓝底块中有红色方块；将 `[32,32]–[96,96]` 定为 child 层，`exclusive:true`、`keepUnder:true`。body 只绑静止 root，child 绕 `(32,64)` 转 90°。这隔离了底层骨骼运动因素。

- 静止时输出正常，探针 `(72,56)` 为 `[232,33,36,255]`。
- body 的纹理在同一探针仍为 `[232,33,36,255]`，说明 keepUnder 的纹理保留确实执行。
- 但 body 网格没有内部探针对应的原有网格点；child 移开后输出探针变成 **`[0,0,0,0]`**，露出透明洞。全程无 GL 错误。
- 无分层的原图对照在此点仍是 `[232,33,36,255]`。[实际对照](66ea5f7/evidence/keep_under_comparison.png)。

**源码根因：** 第 63 行 `inLayer` 对 body 无条件排除所有子层多边形，未检查 `l.keepUnder` / `o.keepUnder`；第 65–70 行因而不为内部区域生成网格。第 111 行虽正确跳过纹理挖洞，保留的像素仍没有对应底层三角形可渲染。

**最小修法建议，尚未代改：** body 的网格纳入规则与纹理挖洞规则使用同一 keepUnder 判断，需要保留底图时同时保留该区域的 body 网格，并确保底层由预期骨骼控制。修后上述探针应保持不透明。保留原像素不等于生成了被遮挡的身体补洞图；原图里的旧手臂/手形也可能留下双影，不能把这项修复宣称成任意大动作无洞、无重影。

## 3. pins：body 内按新语义验证通过，旧“完全忽略”项关闭

新版的语义是“半径内顶点绑定指定 bone，默认 root”，不是世界空间 IK 锁定。本次 root 保持 identity，只令 child 转 90°；pin 为 `{at:[96,64],bone:'root',r:24}`，位于实际网格顶点。

- pin 顶点变形后仍为 `(96,64)`，位移 **0 px**；权重为 root=1。
- 红色标记质心从静止到转动均为 `(95.5,63.5)`；pin 像素保持 `[232,33,36,255]`。
- 删除 pin 的对照中红标记移到约 `(64.377,94.328)`，原 pin 像素变透明。有/无 pin 的绑定数组与输出均不同。[对照图](66ea5f7/evidence/pins_comparison.png)。

第 78–84 行已读取 pins 并覆盖该区域的候选骨骼，固定权重避免平滑改写。**旧 707f1a4 的“pins 完全不读取”不适用于新版。** 这仅验证基本 body 网格上的新语义，不把它当作 IK、世界空间接地或所有分层组合的验收。

### 独立层 pin 的剩余缺口：引用 s07 的消费者复现

root 转交的 s07 审查者已提供 [reproduce_consumer.mjs](pin_layer/reproduce_consumer.mjs) 和 [consumer_reproduction.json](pin_layer/consumer_reproduction.json)。本审已读脚本与结果，确认其声明为 **bind/矩阵级合成复现，没有 WebGL 渲染**；这不是本审追加的浏览器像素实验，也不是角色实片。

其 arm 独立层只允许 `['arm']`，pin `(60,50)` 指定 `root`。第 80 行把 root 从候选中滤掉，第 82 行在候选为空时回退至 allowed，最终 arm 权重为 1、root 为 0。root 不动，arm 转 0.2 弧度后，该点变为 `(59.8006658,51.9866933)`，漂移约 **1.9966683 px**。这与上述 body 测试通过不矛盾：body 的 allowed 包含 root，独立 arm 层不包含。

因此新版应明确 pin 目标与 layer allowed 冲突时的行为：让显式 pin 目标按既定语义优先，或验证并拒绝冲突数据，不能静默回退为活动骨后仍宣称点已固定。此项引用与本审两项浏览器故障一起交付，但证据层级分别标明。

## 历史证据与范围

旧 707f1a4 引擎 SHA256 `ac728b396d33db90176239fd1418e50c9b7532dc26894c6d40ea7c94d3982c10` 的冻结副本、脚本和 [旧结果](results.json) 保留在本目录根下。旧版确有 pin/无 pin 绑定数组及输出完全相同的问题；旧测试旋转的是 root，不能拿这一姿势直接否定新版允许跟随 root 的 pin 语义。

本轮没有展开 >32 骨等额外边界测试，也没有将合成图故障冒称成已观看 g01/x01 合成角色实片。跨尺寸复用是实际可重现的引擎路径问题，建议先修再让同一渲染器轮流接两种尺寸角色。
