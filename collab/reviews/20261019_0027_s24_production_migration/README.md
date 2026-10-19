# S24 原字节生产迁移包

本包仅本地准备，未写远端、未起浏览器或服务、未实渲。来源已审的 60 帧与 S23 跨镜结论由协调方提供；本包只确认结构迁移，生产路径 60/60 实际 PNG 等字节验证仍待已有云执行者完成。

## 唯一生产清单

- `UPLOAD_ROWS.json`：仅 11 行，1 个正文模块、9 张原 PNG、1 个原锁。
- `PRODUCTION_TREE_PLAN.json`：同样 11 个可供协调者串行 create_tree 的 tree_elements。新 JS 为 content，9 图和锁直接使用现有源 blob SHA。
- `payload/js/anim/s24_drawn.js`：生产正文，Git blob `6378d0de144faae92dea7fa22711f1e4c1ae373d`，不是 review 模块 re-export。
- 9 图目标 `assets/chars/x24/F000.png`、F006、F009、F012、F015、F019、F024、F032、F040；`assets/chars/x24/final_lock.json` 原 blob `5ded7dbf5a2db772daf765522e4438b808514348`。
- 固定源 `1e64ae9356d6335430d4783cf4976e1569ed1923`。所有源路径、目标路径、原 blob、目标 blob、SHA256 和字节数在行表内。

开始前通过 GitHub 只读确认协调分支最新为 `67dd8e34698a4bee2e5e7dfde72bc55170210d2b`，目标模块与 x24 目录均无冲突。提交前请协调者按最新 tip 再核目标路径及依赖，勿以云分支旧 S23 替换主分支。

## 精确变更边界

`MIGRATION.diff` 只有 5 行定位替换：3 个相对 import、ASSET_ROOT、final_lock fetch 路径。还原这 5 处后，模块与固定源逐字节相同。首行历史说明和 SOURCE_SCENE_COMMIT 历史字段也按要求保持不动。

动作、相机、exp=0.22、fog=0.5、注册矩阵 [0.70,0,0,0.70,590,20]、sheet23(5,env)、flatMaps(native,0)、FPS=24、DURATION=2.5、FRAME_COUNT=60、持帧 6/3/3/3/4/5/8/8/20 均未改。PNG 没有变换或重编码。

3 个直接共享依赖与原实渲清单完全一致，S23 为修后 blob `7bf079d18839964271c3e743247509ed3840326d`。18 个共享闭包文件均与 93705f2 实渲基线 SHA256 一致。`validation_workspace/` 是本地只读快照，不能上传覆盖共享文件；source_snapshot、tools、qa、说明和账本也不是生产运行依赖。

## 已执行测试

在本包目录运行 `node --experimental-vm-modules tools/check_static.mjs`，短结果为 `qa/local_static_checks.json`，状态 `PASS_STATIC_AND_STUB_ONLY`。

- 11 个生产文件 hash、9 PNG 的原 Git blob / SHA256 与 1024×1536 头信息均通过；锁为原字节。
- 全 60 帧曝光/图片绑定与原模块一致，见 `FRAME_BINDINGS_60.json`。
- 真实主分支 19 模块 ESM 图语法和 import/export link 通过，所有依赖路径可解析。
- 源与生产 renderFrame 在相同三依赖桩、PNG 头信息桩下，60 个控制流/相机/卡片/床单参数方案一致。生产入口只请求 9 个本镜 PNG 和本镜锁，reviews 请求及运行 import 依赖均为 0。
- 锁批准、锁状态、锁 hold/SHA/count、缺锁、缺图、坏图 SHA、错误图尺寸共 9 个拒绝用例通过。

真实共享闭包直接在无浏览器 Node 中 evaluate 会需要 Path2D；本包因此采用真实图 link-only 加入口控制流桩测试，不模拟或声称真实 Canvas/WebGL。任何静态测试都不替代实际 60/60 PNG 对照。

## 云端下一步

`RENDER_COMMAND.txt` 提供现有项目 renderer 的最短命令（默认 1920×1080、24fps、整镜 60 帧）：

    node tools/js/frames.cjs js/anim/s24_drawn.js build/S24_production60 --workers 2

必须复用源审的同一云 Chromium 环境。原环境为 /usr/bin/chromium 加 --enable-unsafe-swiftshader；本包附原样 process-only audit shim 供已有云执行者需要时使用，完整环境调用也在命令文件中。无需重复渲源。

`ACTUAL_BASELINE_60_SHA256.json` 已从固定源 actual_delivery_validation.json 提取全 60 个 actual_Canvas_SHA256，并记录来源路径和 blob；不是 MP4 回解帧 SHA。渲后执行 `python tools/check_actual_pngs.py <实际PNG目录>`，须 60/60 原 PNG 等字节，并核 audit 的 JS/资源错误 0、reviews 网络请求 0。若不同，保留差异停止，不自动改动作/光/资产，不据此登记 ready 或修改 EDL、音频。
