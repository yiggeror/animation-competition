# S08 局部灯机械修正候选

运行文件仅 `lamp_mechanical_candidate.js` 与 `s08_first20_lampfix_candidate.js`。依赖已交 `collab/reviews/20261018_1800_s08_first20_scene/` 的契约、层表和15图层，不复制图片，不修改正式first20或共享helper。

局部lamp相对固定 `0c215550:js/code/s08.js` 仅改 `const la = 0.55 - lift * 0.9;` 为 `const la = -0.85 + lift * 0.5;`。灯其余源码逐字节相同；101个lift采样的全部非杆绘制指令一致；027全部绘制指令和杆端一致。候选从000就使用新高初位，持续至019，020仍拒绝，没有020以后偷接姿态或突跳。

023/025/027杆端分别为 `(1254.039050,737.534976)`、`(1242.151548,750.952730)`、`(1233.953205,766.894374)`；罩升0、41.621622、83.243243px。000=023未压初位。详见MECHANICAL_CHECK.json及SCENE_WIRING_CHECK.json。

`F000_lever_overlay_GEOMETRY_NOT_CANVAS.png/svg`只是新旧杆坐标叠图，灰杆仅旧错误位置对照；实际灯只画一根杆。无真实Canvas新增帧，不用该图冒充接景。

已有云渲环境先核首帧：

```sh
node tools/js/snap.cjs collab/reviews/20261018_1822_s08_lamp_mechanical_candidate/s08_first20_lampfix_candidate.js build/S08_lampfix_F000_1920x1080.png 1920 1080 0
```

确认首帧后按需渲20f（本地未运行）：

```sh
node tools/js/frames.cjs collab/reviews/20261018_1822_s08_lamp_mechanical_candidate/s08_first20_lampfix_candidate.js build/S08_first20_lampfix --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first20_lampfix_1920x1080_24fps.mp4
```

本地测试：在包目录 `npm test`，或 `node test_lamp.mjs` 与 `node test_scene.mjs /path/to/first20/package`。命令比较是mock，不是光栅Canvas。测试会在候选目录写JSON；不改原包。独立审已核单角式、101档非杆指令及027终点。真实帧仍须检查000新高杆与手臂/灯罩遮挡。
