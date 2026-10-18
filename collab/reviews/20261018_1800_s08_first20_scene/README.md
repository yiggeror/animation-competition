# S08 首20帧隔离接景候选

入口 `s08_first20_scene.js`，1920×1080、24fps、20帧、20/24秒。曝光：000×3 / 003×2 / 005×1 / 006×3 / 009×3 / 012复005×2 / 014×3 / 017×3。020及以后明确抛错；不长停、不补后续姿态。

## 冻结来源

- 旧14f模块固定提交 `0c215550edb5f1807b240ca7f79f6f61c8aef01e`，目录 `collab/reviews/20261018_1721_s08_first14_scene/`。此前真实14f渲染提交 `2383f9f1ab8b0e6551ea5c339c8ec32b76f29b5b`，证据路径 `collab/reviews/cloud_s13_20261018/render_assist/s08_first14/`。本包不冒充该次真实结果的新20f扩展。
- F014原母 SHA256 `d1727966cfc41b5a61f91c8b19cf8177fe88f12ce20c7d4a1036305b3fbe3d51`；F017原母 `4e7be236953bee57aa8c3ecfc142893ab15c67095fae4b77718ff6aba0b1ec20`。只复制已审 `F014_LAYER_PARTITION/` 两层及 `F017_LAYER_PARTITION/` 三层，不重新分层、不修改图片、不重复上传整母。
- 旧10层文件逐字节相同；旧曝光行和联系人坐标原值保留。背景/桌/凳/灯函数以及 light/glow/emit/cam 源码块逐字节相同。前14帧的合同56个时点和模块14帧mock绘图调用一致。随机grain仍由原paintshot按绝对t确定，未改helper。

## 新增两态与接触

F014保持手托盒，没有桌面盒层。F017按 `灯、凳、body、桌前沿、table_box、arms` 绘制；1665个可见盒像素只在table_box，人物两层无盒alpha。三层互斥，重建RGBA精确等于原母。014/017采用各自已审新真实手臂分层，未套旧远肘遮罩。人物全部 x=0、y=0、sc=1，无拉伸和位移补动作。

F005/F014/F017的近手柴ROI `[1034,770,1086,832]` 逐RGBA完全相同，SHA256 `72ee6e47113726f578ad2e1fdb523cd022265b75b0a2affed851beb336c72bee`；原图和geometry相互核对，柴头 `(1074,782)`、握点 `(1046,819)`。火、暖光和辉光沿原公式跟柴头。灯罩始终未抬，灯芯始终无火。

F017桌盒alpha bbox为 `[1063,947,1138,971]`（末端不含），alpha>128的最低行970。盒中心 `(1100,960)`、名义底971；原桌面950.2–981、前唇981不动。只在盒层附既有renderPaint的contact接口：`base:970, a:.22, blur:.65, sy:-.055, dx:0, dy:0`。原盒剪影投影的未模糊y范围970–971.265，先画贴附影再画盒，arms随后遮挡；没有独立飘影、人物影或新桌子。

这是极薄接影候选，必须由实际Canvas核实接触读感、前唇层序和014→017换张，不能因几何和mock通过就认定视觉通过。

## 本地验证与真实渲染门禁

本次只完成语法、合同、模块mock、原RGBA重合和源码/文件一致性检查，真实Canvas新增0帧。既知本机Chromium launch因socket Operation not permitted失败；未重试启动、未安装、未绕过。

在仓库根重跑静态检查：

```sh
P=collab/reviews/20261018_1800_s08_first20_scene
node --check "$P/s08_first20_scene.js"
node "$P/test_contract.mjs" collab/reviews/20261018_1721_s08_first14_scene
node "$P/test_module.mjs" collab/reviews/20261018_1721_s08_first14_scene
```

原像素重合审计（只读打开原母，不输出图片）：`python "$P/verify_pixels.py" /path/to/astra_s08_first_mother_20261018_1433`。

现有可用云渲环境最短完整20f命令：

```sh
node tools/js/frames.cjs collab/reviews/20261018_1800_s08_first20_scene/s08_first20_scene.js build/S08_first20 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first20_1920x1080_24fps.mp4
```

如先只核新增6帧，在同一命令追加 `--from 0.5833333333333334 --to 0.8333333333333334`；这只输出编号00014–00019，不能将所得6帧片标为20f片。完整交付仍需20f。

真实门禁：
1. ffprobe确认1920×1080、24fps、20帧、0.833333秒；不得有020或自动补尾。
2. 看原速20f与F013/F014/F016/F017/F019实际解码：014托盒、017落桌、上收远肘遮挡正确；近柴火不跳；灯罩/灯芯不提前动。
3. 看017/019盒底1×/2×实渲：薄影紧贴真实盒底、落在原桌面、未跨前唇、盒只画一次。若影不可读或分离，反馈真实图再调contact，不能静态代签。
4. 若保留旧14f无损Canvas帧，前14张逐像素比较。否则用固定源旧14f入口及同版依赖重渲再比无损PNG；不要拿两次不同GOP的有损MP4解码差异当作源码回归。

## 最小上传

`UPLOAD_ROWS.json`精确列每项本地文件、目标路径、字节、SHA256与Git blob。运行必需仅新增3个JS和5个PNG；旧10层直接复用固定0c215550已存在blob，不上传重复字节。另附轻量package/tests/审计JSON/本说明供核验。无整母、QA大图、重复影片或大包。无共享仓库写入、EDL修改或音轨改动。
