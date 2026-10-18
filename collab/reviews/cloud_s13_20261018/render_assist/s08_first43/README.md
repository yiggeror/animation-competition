# S08 · 首43帧，仅新增041–042

固定源码 `3e291e2544c5879955a1cf4d12c8e80341a1f4c0`，入口 `collab/reviews/20261018_2335_s08_first43_scene/s08_first43_scene.js`，SHA256 `dbe5eea6aa4d244f0caeb8f1cb50d3495b1a44fdc4993b2ce2e49a0a250036e6`。45个固定运行文件均按源Git字节和SHA双核，见 [清单](fixed_runtime_inputs.json)。未改共享源码。

- [43帧静音MP4](S08_first43_1920x1080_24fps.mp4)：1920×1080，24fps，43/24秒（1.791667秒），只有视频流。SHA256 `600840cfdfbba11ee8e9a1de398dbd7457c6de67350197bb95f451de99edd05f`。
- 新增两张**无损原始Canvas PNG直接随片交**：[F041](canvas_new/F041.png)、[F042](canvas_new/F042.png)，与本次实渲和合片前PNG逐字节一致；[原始校验和](canvas_new/SHA256SUMS.txt)。
- [040→041→042实际解码全帧](00_actual_040_042.jpg)、[前后手/侧管/杆座/盒影](01_hands_pipe_lever_box_actual.jpg)、[药头接芯4倍近图](02_match_wick_contact_actual4x.jpg)；三张完整解码PNG在 `decoded/`。

首次新渲041–042后，Astra补充要求捕获实际失败资源URL/状态，故只对新增041–042再实渲一次网络审计；两次原始PNG逐字节相同，未重编码视频，前41帧仍零重渲。合计两次新2帧运行、一次编码。000–040复用 `d1e76b7092d61bf1c01bbbf05077e670a03f0a17` 已核41帧原始PNG，复制前后SHA一致，见 [复用记录](reused41_baseline.json)。没有重渲前41帧，没有扩渲043或提前点芯。

已实际查看原始F041和三张解码全帧及局部：040留隙→041/042药头贴芯顶，火焰接在药头，未见独立灯芯火。近臂/手/柴在侧管前，远手握低杆、杆座及单盒薄影保持。源码wick=0只是辅助，不把火光照亮的芯误判成独立点芯。原层低杆盘148像素RGBA和盒1665可见像素/alpha与038一致，盒底970；原机构lift1、罩升83.243243、角−.35。见 [实际画面复核](author_actual_review.json)。本地接触门通过，待Astra原速复审。

[逐帧核验](verification.json)包含43张源PNG和43张对应MP4解码SHA及RGB MSE，最大9.45454216003418；[ffprobe](ffprobe.json)独验帧数、时长、尺寸、帧率和无音轨。[源码回归](source_contract_check.json)仅表示旧41帧164个子采样状态、绘制函数与旧入口一致，F041停两帧且043拒绝；不替代实际画面证据。

```sh
NODE_OPTIONS='--require /tmp/s08_first27_system_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261018_2335_s08_first43_scene/s08_first43_scene.js build/S08_first43_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.7083333333333333 --to 1.7916666666666667
```

系统Chromium shim只指定 `/usr/bin/chromium`，不改渲染逻辑。首次[原始日志](increment_command.log)只有未标URL的404文本；新增要求后的第二次仅新2帧审计见 [实际URL/状态](actual_network_audit_summary.json)、[完整事件](actual_network_events.jsonl) 与 [补跑日志](network_audit_command.log)。第二次实渲控制台location明确指向 `/favicon.ico`，错误文本状态404；Playwright未发出该请求对应response事件，另以同固定服务器版本做 [只读GET](favicon_read_only_http_probe.json) 实得HTTP404（0渲染调用）。这两类证据分开记载，不冒充同一次响应。关键入口/新层响应成功，0pageerror、0requestfailed。首41历史日志没有URL，无法以新运行倒推其来源，仍记UNKNOWN，不冒称已证明其favicon来源或全资源200。S08本轮生图0；S12同一F000首母任务独立保全，不混入本包。未改EDL、音轨、ready或生产主分支，未启动全片/Blender/新付费API。
