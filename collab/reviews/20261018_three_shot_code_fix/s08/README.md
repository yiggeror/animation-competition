# S08 点灯接触修复

仅实现修改 `js/anim/s08.js`。基线为协调方提供的 50eaff8 文件包；该目录不是 Git checkout。保留 `DURATION = 6` 及 `pose, matchGeom, WICK, leverTip, lift` 全部既有导出。没有修改共享 kit/chars、音轨或 EDL，没有远端写入、生图、浏览器重试或视频渲染。

## 修复

- 实际依赖是 `js/code/s08.js` 的 lamp，本包没有 `js/film/props.js`。灯原点补齐 `TOP−1.1`；WICK 指向实际 `fillRect(-21,-226,42,6)` 黑芯帽顶，未沿用 lamp 返回的旧 `−228` 火焰提示点。命令级测试直接跑 lampLayer，核对真正绘制的芯帽和杆端变换。
- 用 `chars/hand.js` 真实 pinch 握点 `[1.46,−0.2] × NN.palm`。先指定世界手角，再解析反求腕点。右手火柴棍从实际指掌握点伸出4.5cm；撤去旧4次固定点迭代。
- 1.7–1.85秒药头贴芯；1.8秒才起芯火；1.85之后撤离。24fps L41–44接触误差最多6.64e−14px（几何误差，不是编码画面测量）。L45开始离芯。
- 左手0.90先锁杆端，0.95–1.12提罩；3.25开始撤指，3.30前移开；杆与罩保持抬起至3.30，然后3.30–3.40一起落回。24fps L22为闭罩锁杆，L23才开始抬升；L79手已离杆而罩仍抬起，L80–81落罩，L82闭合。
- 火柴只甩一次；盒子0.72、火柴2.8落桌交接连续。3.5–4.25髋后移3cm、下沉1.2cm，双脚世界位置固定，双手收回。

## 验证与边界

从项目目录运行：

```sh
node --check js/anim/s08.js
node --test collab/reviews/20261018_three_shot_code_fix/s08/structure.test.mjs
node collab/reviews/20261018_three_shot_code_fix/s08/metrics.mjs
```

最终12项测试全过：实际drawLamp命令、真实hand握点、24fps接火/握杆、发光根部、交接连续性、骨长、脚锁定、关键参数连续及240Hz有限值/可达性。全镜最大腕目标伸展率0.810560，骨长未改。原始8项回归先跑出7失败，过程日志只留本机；最终数值见 `metrics.json`。

`npm test` 未能运行：package.json 没有 test script。仓内视觉示例仍需浏览器；本轮无像素、遮挡、原速观感或MP4验收结论。必须由Opus渲染后独审，重点复查L20–30、L38–48、L76–85与L90–105。手型在0.78/2.90/3.30有一次性类别切换，腕/手角连续，但轮廓开合仍须实渲判断。

S08源文件SHA256：`02ac0d0ea1b53ac6d876e2fbd7afc9f94641885ca1efa81a3a349e3b97420b43`。
