# S24独立正式Canvas接景入口准备 · 尾态未锁，尚未渲片

入口[s24_drawn.js](s24_drawn.js)只在本独占审片目录，导出`DURATION=2.5`、`renderFrame(ctx,t,W,H)`。九态资源来自798402180f223a73281f7c8a5477cad656c97846的[d08/d09完整包](../d08_d09_final_segment/README.md)，换张仍000×6、006×3、009×3、012×3、015×4、019×5、024×8、032×8、040×20；人物固定B=.70+(590,20)，不翻转、旋转、扭曲或插值。

接景沿现有`js/lamp/s06_key.js`的真实场景渲染，保留原S24世界相机`pos[3.15,1.62,1.12]/target[1.80,.62,.98]/hfov46`、曝光.22、雾.5、`sheet23(3.4+.1*t)`幕上咬嘴状态及原房间/布帘/光源。卡片深度继承原base[1.98,.78,.47]，人物按B在场景卡片层放置；原生RGBA作为固有色，平面普通漫反射材质由同一场景统一照明。没有旧x24人物、旧整图转头动作或额外代码人物。身体接触与手均画外，不新增地面假影。

[final_lock.json](final_lock.json)当前`approved:false`，明确等待Astra对032/040及完整60f人物层双审。入口已真实验证会在加载人物或启动WebGL前拒绝正式渲染。锁定后只登记实际终审SHA与状态`ASTRA_FINAL_DUAL_LOCKED_ALL9`；若最终图改变，须同步资源索引/入口SHA，不能只改批准标志。每张PNG在浏览器用SHA-256核验后再解码，不允许占位图或悄悄跳过丢图。

[19项场景依赖](qa/runtime_source_manifest.json)递归对固定c920857531ac60a63d1b09a848698854856ab657逐字节核对，原S24及共享源码未修改。[Chromium准备核验](qa/preflight_result.json)已实际执行：模块可真实导入、全60帧资源与本地原生PNG SHA映射一致、相机/灯雾/B/边界检查通过，待锁门确实拒绝。该记录是准备核验，**实际场景帧0，正式MP4尚无，不报整镜ready**。最初用Node直接导入触发上游浏览器专用Path2D未定义，改用真实Chromium后通过；未生成假图掩盖。

尾态锁定后的最短正式命令（此刻不要执行）：

```bash
node tools/js/frames.cjs collab/reviews/cloud_s24_20261018/scene_candidate/s24_drawn.js build/S24_scene60 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S24_scene60_1920x1080_24fps.mp4
```

当前云环境需系统Chromium时，沿既有进程级`NODE_OPTIONS=--require <system_chromium_shim.cjs>`，不改仓库渲染器。后续须核完整60帧1080p/24fps/2.5秒、音频流0、源/解码对应；实看全九态尤其024→032→040与末停、头顶净空、双尾/袖边、场景明暗与幕上关系，才能交完整场景候选。灰深底人物层不代替这一步。音轨、共享EDL、生产入口与ready仍归协调统一整合。
