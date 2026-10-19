# S25 浏览器完整144帧：固定提交启动失败，最小导出修正诊断片已交

独立分支 cloud/s25-browser144-05535b7a-20261019，生产基线 **05535b7a3bf0d7777333749c8a773dc2f0aaf28f**。未改生产实现、旧EDL、资产或S20分支。

**原提交浏览器门未过：** 原命令实际运行至90秒超时，0帧；Chromium直接报 `Identifier 'FPS' has already been declared`。js/anim/s25_drawn.js第3行已有FPS，第26行又export const FPS。模块实际HTTP SHA为664342ae72e308129071870bf64df3fa4043910eb64274a242e975d3f2d14ce6。见 BASELINE_RUNTIME.json / BASELINE_BROWSER_STARTUP_PROBE.json。27项独立HTTP资产检查全200且与固定提交字节一致；原模块未能执行，不混称已加载资产。

为不阻画面实审，仅在本审查目录另放 **s25_drawn_export_only_diagnostic.mjs**：把重复声明改为 `export {FPS}; export const FRAME_COUNT=144;`，完整渲染函数及所有渲染代码原字节保持。最小待审补丁 fps_export_minimal_fix.patch 已check可应用，**没有应用到生产**。

实际诊断成片 **S25_export_only_diagnostic_actual144.mp4**：Chromium真实Canvas完整000–143，1920×1080 / 24fps / 6.000s / H.264 yuv420p，无音轨；144帧再完整解码无错。MP4 SHA256 **f7e850d478aad87beaa0af9db20f8c34373ad7969568f5fd98d982842508dd26**。26项模块真实资产响应全200，pageErrors=0；17态重复帧的原始浏览器像素SHA一致。此片是导出修正候选的实际浏览器片，**不是05535b7a原生产门已过**。

已实际看解码 all144 总表和 focus16：029落箱、035/041/044松手、048/056入光锥、064/072/084成狗、106/110/114及126/128/132开合口，143尾态可读；本诊断未见新增浏览器视觉阻断。重点帧是MP4解码原尺寸PNG，焦点表和总表只作缩略导览。

需主协调接回的唯一生产阻断：修重复FPS导出并给新固定提交，再认正式生产浏览器门；无需生图。

正式更新：7de17f543f735f455af2a327d20e88d983ede821已完成正式入口000/064/128三帧、26资源和与原完整实际片逐字节像素等价核验，见 production_smoke_7de17f54/README.md；上述055历史阻断保留，不再是当前正式入口阻断。
