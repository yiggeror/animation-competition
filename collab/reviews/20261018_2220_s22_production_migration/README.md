# S22 原字节生产路径迁移包

状态：本地迁移包已封；源 e2601ed 整镜已由协调方报告双审通过；生产路径 Chromium 实渲等价验证尚未执行。本包不登记 ready，不改 EDL、音频、S23 或共享 helper。

## 立即整合的最小范围

- `UPLOAD_ROWS.json` 是唯一生产行表，共 16 项、5,776,336 字节。
- `payload/js/anim/s22_drawn.js` 为模块正文，不是 review re-export。
- `payload/assets/chars/s22/` 包含 12 张采用 PNG、`resource_map.js`、`resource_map.json`、`tail_lock.json`。
- 12 PNG 的 `source_blob` 已在行表内，可直接引用同仓库 e2601ed 对象，不需要重传 PNG。
- 原始固定提交：`e2601ed4650c831a66a97a4945e3778c6f6cb0dd`。
- 原模块 SHA256：`a5d4596d86e9e8a485b70ad3f567716ee6878637f96236b4003a59c42d659d1f`。
- 迁移模块 SHA256：`4c4073f8a6ece1e91489be9f3f9b5c12c4edb2c847304515446daf98196d73c5`。
- F108 唯一采用 SHA256：`e0d31242883ad1dca5e5ce1c838257228e5d980ace1605ea93e2a31349f5a704`。

不要把 `source_snapshot/`、`validation_workspace/` 或 QA 脚本当成生产运行依赖。16 项以外均为本包审计/验证材料；没有修改共享文件的条目。

## 变更边界

模块只有 1 条首行说明、3 条 import 路径和 1 条 tail_lock URL 改动，见 `MIGRATION.diff`。将这 5 处归一回原文，整个模块与原始模块逐字节完全一致。画面、曝光、机位、光、颗粒、人物尺度以及 `sstep(1.5+k,1.82+k,t)` 龟步表达式均未改动。

资源映射 JS/JSON 仅将 12 URL 替换为 `/assets/chars/s22/Fxxx.png`；其余配置、帧窗、持帧和 SHA 未动。12 PNG 与 `tail_lock.json` 原字节保留。tail_lock 的 `approved` 仅表示尾态资产锁，不能替代生产路径实渲与整镜审核；其中 `approval_evidence` 是源包相对路径的历史元数据，不由运行模块读取。来源可在固定 e2601ed 的原路径追溯。

生产模块运行闭包：本模块 → `assets/chars/s22/resource_map.js`、`js/lamp/turtle.js`、`js/puppet.js`；turtle → `js/lamp/crane.js`；实际 fetch 仅为本镜 12 PNG 和本镜 tail_lock。没有运行时 reviews 依赖。3 个共享 helper、`dev/view.html`、`tools/js/serve.cjs`、`package.json` 均已与本地协调提交 a4b00a05 比对相同；只读快照，不上传替换。

命名参照现有 `js/anim/s10_drawn.js` + `assets/chars/g10/` 及 `js/anim/s13_drawn.js` + `assets/chars/x13/`；S22 为两手完整组稿，使用本镜独立 `assets/chars/s22/`，与 s01/s04 场景组目录形式一致。源与协调提交及本地祖先目录未发现 AGENTS.md。s13 的协调 blob 本地不可直接读时，使用已有本地文件并核对 Git blob SHA `a7556d6c843e4e1f55fa3f7b4f38ea5db3b338d8` 与协调树精确一致。

## 已执行的本地验证

`node tools/check_static.mjs` → `qa/local_static_checks.json`，结果 `PASS_STATIC_ONLY`：

- 16 目标文件 SHA/尺寸全部一致，12 PNG 均为 1672×941 RGBA8；未重编码。
- 使用原字节共享 helper 的真实 Node ESM import 成功，导出接口一致。
- DURATION=5、FPS=24、TOTAL_FRAMES=120；120 帧逐项曝光相同，所有曝光边界与输入钳制相同。
- 模块归一后完全等于固定源；资源映射仅 URL 变化；tail_lock 完全等字节。
- 文件 fetch / PNG 头读取桩下 preflight 成功，生产预检 13 请求均仅访问 assets/chars/s22。
- PNG SHA 损坏、尾锁未批准、F108 尾锁 SHA 不符，均按原模块守卫拒绝。
- `node --check tools/verify_cloud.cjs` 与 Python 语法检查通过。

这不是实际浏览器图片解码、Canvas 渲染、视觉审查或成片通过。没有实际 Chromium、生成新图、远端写入、fetch、checkout 或安装依赖。所有 git 读使用 `GIT_NO_LAZY_FETCH=1` + `git --no-lazy-fetch`，只读既有对象。

## 最短云端实渲命令

在已整合 16 项的授权云端仓库根目录，使用项目已安装的 Playwright/Chromium/ffmpeg：

```bash
node tools/js/frames.cjs js/anim/s22_drawn.js collab/reviews/20261018_2220_s22_production_migration/scene120/frames --fps 24 --w 1920 --h 1080 --from 0 --to 5 --workers 1 --mp4 collab/reviews/20261018_2220_s22_production_migration/S22_production_scene120.mp4
```

该命令只生成实渲，不独自证明等价。建议直接使用下述一条严格命令，只实渲生产 120 帧，与 e2601ed 已交原 Canvas PNG SHA 账本逐帧比对并回解实片。

## 严格云端实渲等价验证

由唯一协调者另将 `QA_UPLOAD_ROWS.json` 所列证据放入 `collab/reviews/20261018_2220_s22_production_migration/`，运行：

```bash
node collab/reviews/20261018_2220_s22_production_migration/tools/verify_cloud.cjs
```

此脚本在调用前检查 16 运行项与 6 共享依赖的字节 SHA；默认只通过 `dev/view.html` 捕获生产 120 帧，并与 e2601ed 已交原 Canvas 120 帧 SHA 账本比较。优先在原来源的同一云端、同一 Chromium 环境执行，不重复渲源 120 帧。生产页任何 `/collab/` 网络请求将直接失败。不会读写 EDL、音轨、ready、共享 helper 或其他镜头。

默认门槛：12 图资源 SHA 正确；资源/JavaScript 错误为 0；生产运行 reviews 请求为 0；与固定历史账本 120/120 Canvas PNG 原字节相同；输出 1920×1080、24 fps、120 帧、5 秒无声 MP4；ffprobe 核验后回解 24 张状态首尾帧。历史 SHA 不一致即保留诊断并停止，不自动多渲一次。

仅在无法复用来源 Chromium 环境、需要区分环境序列化与代码差异时，协调者可显式选择 `S22_COMPARE_MODE=paired node collab/reviews/20261018_2220_s22_production_migration/tools/verify_cloud.cjs`。该诊断才会同时渲生产与固定源各 120 帧；原源模块及 helper 来自原字节快照，基线页的原 PNG URL 映射到已证明同字节的生产 PNG。此模式的通过结论仅是同运行时对照通过，不冒充历史 SHA 一致。
输出为本证据目录下全新带时间戳的 `cloud_actual_*`，含原帧、MP4、`decoded_actual/`、`canvas_comparison.json`、`actual_cloud_checks.json`。默认不覆盖任何旧结果。可用 `CHROMIUM_PATH` 指向云端已有浏览器；脚本不安装软件。脚本成功也只证明路径迁移的实际渲染等价，不自动宣告 ready。

## 协调方最新状态

2026-10-18 22:25 UTC 协调方通知：“源e2601ed实际120f现已双审通过（我view四起点/尾119），待生产迁移验证。”这是源包状态更新；本地先前静态测试 JSON 的 `whole_scene_visual_review: PENDING` 保留为当时记录。当前唯一未完成门为生产路径云实渲迁移验证及其协调验收。
