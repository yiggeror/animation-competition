# S24 生产迁移 · 实际60/60原PNG逐字节一致

**验证通过。** 固定生产提交 **`af005f039ef0155ac93c2ff86c5a804cb8aac7ff`**，唯一运行入口 `js/anim/s24_drawn.js`。本轮只实际渲染新生产60帧一次，1920×1080、24fps采样、2.5秒；没有重渲旧基线，没有再次生图/重编码视频或产生声音。完整结果见 [actual_production_verification.json](qa/actual_production_verification.json)。

## 原始字节证据

新生产000–059的60个原Canvas PNG，全都与源审 `1e64ae9356d6335430d4783cf4976e1569ed1923` 的60张缓存文件做了**实际bytes==bytes**比较，并各核SHA256；60/60相同，差异0。给定 [基线表](qa/ACTUAL_BASELINE_60_SHA256.json) 又与原提交的validation原Git blob/SHA、原60张缓存逐一复核，不是用MP4回解帧当基线。

[60帧逐条JSON](qa/all60_byte_comparisons.json) / [CSV](qa/all60_byte_comparisons.csv) 保留生产SHA、批准基线SHA、字节相等标记、实际曝光/原图SHA。原60帧只读，见 [缓存复核](qa/baseline60_cache_recheck.json)。完整新生产PNG留在本工作区 `build/S24_production60/`，旧缓存留在 `build/S24_bite_fix_93705f2_scene60/`。

[生产实渲九态表](actual_production_samples/00_all9_production_actual.jpg) 已实看，另附本次原始生产Canvas样张000/024/059。末059嘴喙仍接触，与已审原片完全同字节。

## 生产请求和共享S23

[完整实际网络/帧事件](qa/actual_network_events.jsonl) 记录 request、response URL/状态、console location及每帧Canvas SHA：

- reviews 网络请求 **0**，无运行import/fetch落向reviews。
- 九张生产PNG在两个工作页共 **18次响应全部200**；原锁 **2次响应全部200**。实际生产入口逐图校SHA后才建图。
- 生产JS/素材全部已观察响应为200；pageerror **0**，requestfailed **0**。
- 控制台一条404明确location=`/favicon.ico`，原样保留；不冒称所有浏览器请求均200。
- 共享S23实际请求200，源内容Git blob严格为 **`7bf079d18839964271c3e743247509ed3840326d`**，与修后93705f2一致；没有拿云分支旧S23覆盖。

[固定运行源清单](qa/fixed_production_runtime.json) 共34项；18个共享闭包与原实渲源SHA一致，九图与原锁逐字节一致。生产正文反向还原5处定位替换后与已审独立入口全文逐字节相同，动作/相机/注册/光/holds/sheet23(5,env)均保留。没有改生产源码、9图或原锁。

## 实际命令与复核

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s24_20261018/production_migration_af005f0/tools/production_audit_chromium.cjs' node tools/js/frames.cjs js/anim/s24_drawn.js build/S24_production60 --workers 2
```

使用同一 `/usr/bin/chromium` 加 `--enable-unsafe-swiftshader`。默认24fps/1920×1080在实际60帧及时间戳中再次核实。审计shim只记录生产调用和选择浏览器，不修改渲染逻辑。[原始命令日志](qa/actual_render_command.log) 与 [核验输出](qa/verification_command.log) 保留。

复核工具为本包 `tools/verify_production60.py`；须在固定af005f0生产工作树与保留的新旧缓存中运行。源迁移README提到的工具未随af005f0上传，因此本包核验器独立执行真实字节/输入/网络门，未把静态桩结果当实际验证。

本云分支只新增本review证据，不携带共享生产覆盖。**ready、EDL与音轨均未写，交Astra统一最后ready给Opus接声。** 未渲全片或运行Blender/新付费API。
