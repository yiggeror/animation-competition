# S29 1号Pro正确整段：生产前段已接，ending源码包待补

**000–239的工程链已接到正式`js/paint/shots/s29.js`，并通过五张实际关键帧检查。完整272帧原字节视频也已保全，可交后续剪辑；当前工程仍不能完整重渲240–271。**

正确视频：`incoming_library/S29_COMPLETE_REPAIRED_11s08f_1080p24_SILENT.mp4`，4,325,635字节，SHA256 `b22ccbd7c6592dcb5b2a4a2fbbfbc27270211f24c6ebe09ed0d0224ab566df13`，Library `libfile_5f9cc973f474819199f45c191c4e9e3a`。272帧／24fps／11秒8帧／1920×1080／静音；没有重新编码或裁切。

正确制作增量：`incoming_library/S29_FULL_REPAIR_INCREMENT.zip`，34,117,143字节，SHA256 `2db66c9a7558b0a48780e64dcff17e9a1a01fccce6186d08ba816f205e1b7739`，Library `libfile_5af75a6f55008191a31652d913dfcc38`。其中16张production、5张raw、完整提示词、mask、来源记录和代码diff原样保留。没有取回2号错误前段。

## 实际接入

先在独立临时树按d7f6→完整制作补丁→花衫色修补丁→公开38bee256尾动作增量的顺序还原；复用本地38bee256／f8ada6aa提交，不重复下载11图尾包。得到47个非新ending的已知基线对象，与最新包BASELINE逐项一致。入口因上一轮结尾模块／压时尚缺而与BASELINE原字节不同，已明确适配，未伪称原SHA匹配。

在这条累计链上按上下文应用最新版5个代码文件的hunks和16张精确生产PNG，再以d7f6作共同基线对当前个人分支逐文件三方合并。最终改变6个S29 JS文件，接入42张累计生产PNG；16张最新版逐字节与包内一致。`CONTEXT_MERGE.json`保留合并前／后／基线SHA及素材清单，`RECONSTRUCTED_BASELINE_CHECK.json`保留基线比对。没有整份旧入口覆盖。

保留F116切宽、F132手机亮、F195–203小满回头、F240准备吹灯节点。入口DURATION按已交片设272/24；全片音轨／EDL没有修改，交总协调处理后续时间线。S30冻结素材与`js/paint/shots/s29_lamp.js`共用冻结头保持原字节，见`FROZEN_S30_GUARD.json`。

## 必要验证

通过项目原`dev/view.html`加载正式入口，逐帧解析000–239曝光路径、核素材存在及声明SHA，和最新版曝光表一致。只实际渲F000／102／126／172／239五张，不重渲整段。前段未请求ending模块／准备图，实际关键帧无页面或资源错误。

`PRODUCTION_KEYS_VS_APPROVED_VIDEO.jpg`左为用户已确认视频的选帧，右为当前正式入口输出，已目视核对场景／人物／道具／机位。它们吻合；每通道像素平均差约1.70–1.95，包含已编码视频的色度／压缩差异。此处只验工程复现，不重新审用户已确认左臂、不重复错误稿审查。实际PNG及运行记录在`actual_keyframes/`。

本检查可在新输出目录复现（当前特意验证ending缺失边界，不渲全片）：

```bash
NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules \
S29_KEY_OUTPUT_DIR=/tmp/s29_production_keys_new_output \
node collab/reviews/cloud_s29_production_integration_20261020/verify_production_keyframes.cjs
```

## 唯一未齐依赖组

等待1号Pro的`S29_ENDING_PREPARATION_INCREMENT.zip`。精确缺项见`MISSING_ENDING_DEPENDENCIES.json`：完整`js/paint/shots/s29_preparation_drawn.js`（预期SHA `629194244d05c9ac0ec8b46b3b105c4dbf26f0aca526344e35dd87530b1303af`）＋9态准备画＋其27张normal／material／shadow派生图，共37个已知基线文件。文件名与预期SHA均取自实际BASELINE，没有按SHA伪造文件。

为使000–239实际可用，入口仅在F240才动态导入这个真实模块；当前F240明确报`S29_ENDING_PREPARATION_MISSING`，缺失模块的404是本次边界负向检查的预期结果，没有调用旧单画结尾。新模块应导出`renderPreparation(ctx, localTimeFromF240, width, height)`；补包到齐后按原路径放入完整模块及其运行素材，核消费映射后再实查240以后／239→240，不需要改回旧入口。

本轮以完整名和简称查Library均未返回ending包，尚未收到，不把检索无结果当作Library不存在的证明。已知输入的完整包和颜色包下载原件在本机保留但不重复提交，Library身份／SHA在`LIBRARY_ORIGINALS_RECEIPT.json`；正式生产素材已直接进入Git，复现000–239不必再找这些旧ZIP。

环境在本轮核查时已可用；已完成实际接入与五张关键图，不以此前S14交付代替本任务完成。完整制作源码目前只差上述ending依赖组，原字节整片可用。
