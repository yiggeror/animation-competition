# S08 首75｜新增064–074实际Canvas

固定源 `1e68c985680596a8c73aee612640c4409584da35`；入口 `collab/reviews/20261019_0309_s08_first75_scene/s08_first75_candidate.js`，SHA `010400f5117de83205b3c7c9b31c4aa4b7393fcb666274fe3009d555957b6bca`。104个包内路径及8项公共运行文件渲前核对固定 Git 原字节，渲后再次核对；共享源未改。

- [75帧实际无声片](S08_first75_1920x1080_24fps.mp4)：1920×1080、24fps、3.125秒，单视频流；SHA `fe6ee5db50fd3a803dca163d1b3f64d51b0e8e8d7084fe9b742f60efd67fb268`。
- [全部11张新增无损Canvas](canvas_new/) 及 [SHA](canvas_new/SHA256SUMS.txt)。旧000–063复用固定 `3324ea3c9adc76805f3fd0d5a1f5d95fa8717bec` 的原Canvas缓存，逐张核SHA、复制后核原字节；未重渲旧帧。
- [063/064/065/066/068/069/071/072/074实际解码](00_actual_selected9.jpg)、[放柴／松指／撤手／桌前薄影2倍](01_table_hands_shadow_actual2x.jpg)、[烟根／芯火／远低杆2倍](02_smoke_wick_actual2x.jpg)，9张完整解码PNG另在 `decoded/`。

已实际看图：064继续下放，066柴触桌，069松指，072空掌撤离；完整臂腕衔接与桌前遮挡成立，布边没有冒片，薄接触影未见越过981前唇。066起桌柴和烟根固定 `(1253.6806826223356,954.1901186474938)`；064/065仍随持柴手在 `(1282.6806826223356,928.1901186474938)`。烟线继续变化，旧位无第二根；独立芯火持续、柴未复燃，单盒／贴底影／远手低杆保持。[实看记录](author_actual_review.json) 仅签此增量，待 Astra 整合审查。

[验证](verification.json)：全部75源PNG逐帧与实际视频解码比较，最大RGB MSE `9.812417984`；浏览器直接PNG、合片源与11张交付PNG的SHA全同。实际只渲一次064–074、编码一次；075未含，不另渲首66/69，没有新生图。

[实际资源日志](actual_network_events.jsonl) 与 [摘要](actual_network_summary.json)：15张新层在两工作页共30次响应均200，0 pageerror、0 requestfailed；26项成功运行文件逐项与固定Git原字节一致。console 的唯一404实际URL为 `http://127.0.0.1:41815/favicon.ico`，原记录保留。静态256个旧子样、57旧层／15新层SHA及原光火烟调用回归通过，未以静态检查替代Canvas。

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first75/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0309_s08_first75_scene/s08_first75_candidate.js build/S08_first75_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 2.6666666666666665 --to 3.125
```

私有分支 `cloud/s08-first75-render-20261019`，只交本目录。未改共享实现／留言／ready／EDL／声音；未推共享主分支。
