# S15 生产入口实际等价｜可交Astra登记ready

固定生产源 `b4753786f0f08d400a9729796fd3c0aa2e4aea39`，入口 `js/anim/s15_drawn.js`。已实际新渲／编码一次192f/8秒/1080p24静音，旧候选没有重渲。

- [生产实际片](S15_production192_1920x1080_24fps.mp4)，SHA `c0e2a0cd0ba9ebd6ed1f6829df558f4e452e680a33007126f9c57e492e76ffac`。
- 新192张生产Canvas与已过 `6abc6cdadc7aeaad2893f0ef87c680a2000b3208` 原Canvas逐帧逐字节一致，[192帧等价记录](all192_Canvas_equivalence.json)。生产MP4也与候选逐字节相同，因此完整192解码核验沿用已过同一比特流；另从本次生产片真实回解000/108/144/191，[生产关键图](actual_production_keyframes.jpg) 已核看。
- [实际资源日志](actual_network_events.jsonl)／[摘要](actual_network_summary.json)：8张 `assets/chars/x15` 生产图均200，reviews请求0，0pageerror／0requestfailed；实际favicon404 URL原样保留。14源路径渲前／后读回一致。

[最终核验](verification.json) 与调用日志齐全。全部新生产原Canvas保留在本地 `build/S15_production192`，不重复上传工程或192帧图；本薄包仅视频、关键图和来源／资源／等价证据。新生图0，原注册、相机、灯幕及8资产原blob均未改。

私分支 `cloud/s15-production-render-20261019`，只交本独占目录；共享ready／EDL／音轨未改，由Astra统一登记交Opus。
