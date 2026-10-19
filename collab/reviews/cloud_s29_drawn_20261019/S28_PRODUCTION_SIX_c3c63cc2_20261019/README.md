# S28 生产迁移六帧实际核验 · PASS

固定生产源 `c3c63cc288807740114a4689af6ea18277a63794`，独立分支 `cloud/s28-production-six-20261019-c3c63cc2`。仅执行一次原 `scripts/verify_s28_migration/verify_six.cjs`，执行器和生产文件未改。资源观察预加载只记录事件，Chromium启动参数原样保留。

实际000/012/042/132/162/191六张1920×1080 PNG，全部SHA256与脚本冻结2051e3fa基准一致；64运行依赖blob、原曝光和全部192路由检查通过。原始比较结果见 `PRODUCTION_SIX_CHECK.json`，六PNG在 `actual_six_png/`。浏览器41请求/41响应全部200，无请求失败、页面或控制台错误，没有review资产请求。日志、PID和退出码均归档；唯一node PID67436已正常退出0，HTTP由本次runner退出清理。

六PNG均已实际打开：前三帧舞台手势变化，132起为插线手机1%充电画面，162/191延续。这里只证明改址迁移等价，不新增完整192帧美术签，不改ready、音频或原完整MP4。原完整MP4仍是 `/tmp/s28-full192/S28_FULL192_24FPS_8S.mp4`；旧核验引用另存，本轮没有重渲192帧、没有imagegen。

复现需新空输出目录及空闲8198端口，按 `run_six_UNMODIFIED.sh`；此交付已完成，不应无故再次执行。来源哈希见 `SOURCE_SHA256.json`，所有新增交付文件见 `MANIFEST_SHA256.json`。
