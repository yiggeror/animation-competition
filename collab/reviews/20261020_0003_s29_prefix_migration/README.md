# S29 已锁036–071纯路径迁移候选

只接六张已过完整RGBA，逐字节复用原blob；原机位、灯、幕、手机、地影原指令保留。36帧静态场景指令及6组原云合成指令一致。此模块是部分区间，000–035和072以后主动报错，EDL/原s29.js/音轨均未修改，不能当整镜ready。

23:25重新冻结的后段时点：4.8切宽、5.5手机、8.1–8.42回看、10后靠灯仍保留；本包未验证其人物，不能让旧warp作替代。早段000/024/030正式注册与曝光缺项见MISSING_EARLY_PREFIX.json，原云正核已有实件。

## 现有云唯一12PNG等价门
固定本提交，仓库根执行（只用已安装Playwright/Chromium）：

`NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node collab/reviews/20261020_0003_s29_prefix_migration/render_few.cjs --repo "$PWD" --playwright /opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright --frames 36,41,42,47,48,53,54,59,60,65,66,71 --out /tmp/s29-prefix-production12`

执行器自启临时HTTP、只以上12帧、输出目录非空即停止防重复。运行前后逐字节核六锁图/三正文/三个原支持/控制JSON。Canvas PNG对各帧原实际SHA逐个比对；不一致保失败证据，不自动重跑或降阈值。原对照036–048来自baf6d568；后段来自55942c39与仅060–065替换的93fa4af2，不引用S28片。

生产运行路径仅js/anim/s29及assets/chars/s29，原paintshot与两个共用资产只核不改；验证执行器在本审查目录，不成为运行依赖。全部6张原图无生成/调色/变形；真正浏览器等价尚待此12帧门。
