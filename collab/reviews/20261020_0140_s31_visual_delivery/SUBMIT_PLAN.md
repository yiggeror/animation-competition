# S31 最小生产入口准备

仅需新增生产文件：js/paint/shots/s31_drawn.js（payload/ 下原相对路径）。现有 S28 也是薄 export wrapper。该文件直接导出已审冻结 candidate 的 render/renderFrame、DURATION 与诊断接口，FPS=24；不复制实现，不改任何渲染常量。

依赖：现存 collab/reviews/20261020_0031_s31_complete336_gate 的冻结40文件必须继续随部署发布，不可被部署过滤。新wrapper相对路径 ../../../ 回到仓库根，原候选 import.meta.url 完全不变，17图像URL和原B冻结模块路径完全不变。此方案有意依赖审查包以避免迁移引起行为差异；以后要去除collab部署依赖须单独做等价迁移核验，不能先移文件再宣称等价。

本地已核：40/40文件SHA相同；递归21 JS模块、36条import/export边全部可解析，21模块ESM语法全过。原B正式 s31.js 与冻结副本逐字节相同。dev/view.html 按 mod.render 或 mod.renderFrame 加载，此wrapper保留两个接口。

Node ESM导入stub验证通过：21模块成功link/evaluate；wrapper两导出与冻结候选函数引用严格相同；DURATION14/FPS24、全部180绑定、B180不走A、杆长有限均通过。仅构造最小Path2D/Canvas stub承接模块初始化，22个假context，不产生像素、没有Image加载、没有调用render/renderFrame。见NODE_IMPORT_STUB_CHECK.json。此为接口/模块检查，绝非浏览器或渲染等价证明。

实际浏览器加载门仍缺失：默认Playwright浏览器未安装；系统Chromium启动报socket Operation not permitted，已停止该路线，不尝试绕过执行限制。后续仅可在 Opus 已授权现有集成环境核验，禁止恢复三云；check_load_only.cjs仅保留为未通过检查工具，不代表执行授权或通过结论。

提交清单：
1. 新增 js/paint/shots/s31_drawn.js。
2. 审核记录可选：本计划、STATIC_LOAD_GRAPH_CHECK.json、ORIGINAL_B_PRESERVATION.json、fixture_sha_check.json、NODE_IMPORT_STUB_CHECK.json、check_import_stub.cjs及已有全片视觉报告。不要把load_fixture重复40文件再提交。
3. 待零渲染正式加载检查通过后，由主协调决定ready记录；本任务没有修改ready。
4. EDL仍保持原 s31.js，待主协调/Opus按原14秒/7.5秒切点把mod改为s31_drawn.js，另核音频；本任务不修改EDL、声音或远端。

不建议重复完整336渲染。原实物SHA已独核，但本次只证明薄wrapper函数同引用、资源路径未变，没有实际浏览器加载门，不夸大为wrapper已实渲等价。
