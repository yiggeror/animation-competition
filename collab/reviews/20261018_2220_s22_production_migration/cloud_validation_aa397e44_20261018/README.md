# S22固定生产迁移：云端实际验证通过

固定被测提交：`aa397e44887e47d395b699fdba92cbd7795a9001`；原Canvas账本提交：`e2601ed4650c831a66a97a4945e3778c6f6cb0dd`。运行原始命令`node collab/reviews/20261018_2220_s22_production_migration/tools/verify_cloud.cjs`，默认historical，仅捕获生产120帧一次。**结果：PASS_HISTORICAL_CANVAS_EQUIVALENCE_ONLY，120/120原Canvas PNG逐字节一致。** 未重渲旧120，未执行paired模式，无自动重试。

[完整实际验证JSON](../cloud_actual_20261018T223428507Z/actual_cloud_checks.json)、[逐帧比较及全部HTTP](../cloud_actual_20261018T223428507Z/canvas_comparison.json)、[关键原始运行日志](verify_cloud.log)、[运行环境与脚本SHA](run_environment.json)、[独立汇总核验](verification_result.json)。生产模块SHA `4c4073f8a6ece1e91489be9f3f9b5c12c4edb2c847304515446daf98196d73c5`，脚本原字节未改。

- 120张新生产原帧逐一重核SHA，与固定e2601ed账本完全相同；源账本快照也复用原Git blob。
- 12张资源均1672×941、SHA一致；12 PNG与tail_lock均复用源Git blob，[身份检查](locked_blob_identity.json)。
- 生产运行22个HTTP请求全部200，reviews请求0、JavaScript/资源错误0；运行路径只有dev入口、生产js与assets，无collab运行依赖。
- [新生产实景MP4](../cloud_actual_20261018T223428507Z/S22_production_scene120.mp4)：1920×1080、24fps、120帧、5秒，无音轨。视频也与源片逐字节一致，完整SHA为`2370ae5b951a98e22ab1ece6ab082f4c0489850e0f614a43a59728f2b01378d2`。
- [120张生产原帧](../cloud_actual_20261018T223428507Z/frames/)与[24张实际状态首尾解码图](../cloud_actual_20261018T223428507Z/decoded_actual/)保留。已实际打开生产解码036、108、119，见[看图范围记录](production_frame_spotcheck.json)。

关键日志保留`production:24/120`至`production:120/120`及最终PASS/120匹配JSON。Node v24.19.0，Chromium154.0.8037.57；没有安装软件或新生图。该工作区在固定aa397e44建立，既有生产/共享文件全部未改，新增内容只有本次cloud_actual与cloud_validation证据目录。

本结果仅交迁移实渲一致性验收；**未改EDL、音频、ready或生产主分支，最后ready由Astra统一登记。**
