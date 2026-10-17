# 942df5d 引擎修复复验：三个原案例

**结论：本轮三个原案例通过。A→B→A 跨尺寸空白阻断关闭；逐层 `keepUnder:true` 的底层网格缺失关闭；body 内绑定 root 的 pin 保持有效。** 旧版结果保留于上级目录，本报告只约束以下固定源码和原案例，不扩大为人物动画或所有引擎功能通过。

## 身份与方法

- 固定提交：`942df5d2701966c483902c7c0edb9bd3b7b2196b`。
- [冻结 warp.js](source/warp.js) SHA256：`7576db53c333c505bfe8d8ad8c179742cffc1293d49dca6416f1db6ea23e5deb`。复验末主仓 HEAD 和源码哈希仍与此一致；[身份记录](identity.json) 保存源码、脚本和结果哈希。
- 实际 Chromium `154.0.8037.57` / WebGL 2 / ANGLE SwiftShader，继续使用原 66ea5f7 测试的合成图、尺寸、骨架、pin、图层与姿势。没有改引擎、仓库或人物图，没有新批渲。
- [复现脚本](reproduce.cjs) 跟踪实际 `viewport` 调用接收的 GL 对象，以确定当前上下文；每次 render 后对**全部已创建上下文**逐个 `getError()` 至无错，并在 [results.json](results.json) 的 `contextErrorDrains` 中保留上下文 ID/尺寸/错误数组。未沿用旧脚本“最后创建的上下文就是当前上下文”的假设。
- 全部 11 次测试/对照 render 的所有上下文错误数组均为空；浏览器 console 与 page error 均为空。三张对照图已实际查看，原始透明 PNG 保留。

复跑命令：`node /tmp/laidian-rig-engine-audit/942df5d/reproduce.cjs`。脚本自动启停本地 HTTP 服务和浏览器；[run.log](run.log) 保存本次输出。

## 1. A→B→A：原空白阻断关闭

绑定 A=96×64、B=64×96，均为单骨、identity pose；再次画 A 时仍使用首次 A 的同一绑定对象。

| 调用 | 实际当前上下文 | 不透明像素 | 所有上下文 GL 错误 |
|---|---:|---:|---|
| A 首次 | 2 | 1536 | 无 |
| B | 3 | 1536 | 无 |
| A 再次，同一绑定 | **2，复用原上下文** | **1536** | **无** |
| A fresh-bind 对照 | 2 | 1536 | 无 |
| 对照绑定再次渲染 | 2 | 1536 | 无 |

首次 A、再次 A、fresh-bind 及重复对照的 PNG SHA256 均为：
`baf41cd4af37ae76f590f4e091cbc5b1d959fa2b4943182d9c0dff40be7b288b`。

因此原 66ea5f7 的第三次 A 全透明及 `INVALID_OPERATION` 不再出现。[实际对照图](evidence/context_comparison.png)。源码第 138–147 行的 `GLCS` 按尺寸保留上下文，第 182–192 行的 `L.vaos` 按 key 取对应 VAO，与实际 ID 2→3→2 的结果一致。

## 2. keepUnder：原透明洞关闭，保留像素语义得到验证

复用原 128×128 合成图与 child 方形层，`exclusive:true`、逐层 `keepUnder:true`，body 只绑静止 root；child 绕 `(32,64)` 转 90°。

- 原故障探针 `(72,56)`：body 网格现在存在该实际网格顶点；旧版为不存在。
- body.tex 探针保持 `[232,33,36,255]`。
- child 转开后，输出同一点也保持 **`[232,33,36,255]`**；旧版此处变成 `[0,0,0,0]`。
- 当前实际上下文为最早创建的 128×128 上下文 **ID 1**，并非最后创建的 ID 3。所有 GL 错误均为空。

第 63 行 `inLayer` 已对 keepUnder 子层保留 body 网格，第 107–118 行的纹理处理也保留该区域。[实际对照图](evidence/keep_under_comparison.png) 显示原缺网格导致的内部透明洞已消失。

通过范围是“底层网格与原像素均保留”。合成图中原红块仍在原位，移出的 child 又画出另一块红色；这正是保留原像素的结果，**不等于补出了原图中被遮住的身体，也不证明真实手臂大动作没有旧影/双影**。

## 3. body pin：原新语义案例无回归

root 保持 identity，只转 child 90°；pin 为 `{at:[96,64],bone:'root',r:24}`，网格 step=8。

- pin 顶点仍为 `(96,64)`，位移 **0 px**，root 权重为 1。
- 红色标记质心从静止到转动均为 `(95.5,63.5)`；原 pin 像素仍为 `[232,33,36,255]`。
- 无 pin 对照质心移至约 `(64.377,94.328)`，原 pin 像素变透明；说明测试确实驱动了活动骨，并非没有运动。
- [原像素输出对照](evidence/pins_comparison.png)，无 GL 错误。

这里只确认 body 内该 pin 案例。独立 layer 的 allowed 排除 root 时的旧缺口由 s07 另行复测，本报告不抢先宣称其通过。pin 仍是绑定骨权重语义，不是世界空间 IK。

## 关闭范围

以上三项按原复现案例关闭，旧 66ea5f7 失败记录不覆盖、不删除。没有追加其它边界测试；新增 `renderMaps` 路径、真实 g01/x01 合成与动作表现不在这次三个案例的验收范围。
