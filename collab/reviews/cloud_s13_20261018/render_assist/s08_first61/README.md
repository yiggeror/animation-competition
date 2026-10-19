# S08 首61 · 只增058–060实际Canvas

固定源`b99ce952dbdd6efc65344bf70c159b2cebebc612`，入口`collab/reviews/20261019_0207_s08_first61_scene/s08_first61_scene.js`，SHA256 `8d240c2959e9f2f14ba801fb247df3e3a707a6457f5c6acb4b3ba1bf3404f09f`。源提交71路径、57项运行清单均核Git字节，渲后与静态测试后复核未变。

- [61帧实际无声片](S08_first61_1920x1080_24fps.mp4)：1920×1080，24fps，61/24秒。SHA256 `41f9ee2d87d9103904c240094521293e99112c6840495008ea13d9a0d6b6122e`。
- 三张新原始无损Canvas：[F058](canvas_new/F058.png)、[F059](canvas_new/F059.png)、[F060](canvas_new/F060.png)，[完整SHA](canvas_new/SHA256SUMS.txt)。与浏览器输出及合片源PNG相同。
- [057→058→059→060实际视频解码](00_actual_057_060.jpg)、[药头烟根/芯火4倍](01_smoke_root_wick_actual4x.jpg)、[双手/低杆/单盒2倍](02_hands_low_lever_single_box_actual2x.jpg)；4张完整解码PNG在`decoded/`。

只1次渲058–060、1次编码。旧000–057按`2ee2133d0966eab25c5b2bbb1be40d768f45b8b8`首58的实际Canvas逐SHA、复制后逐字节复用，[清单](reused58_baseline.json)。未重渲旧帧，未渲061+；没有新生图。

实看057→058整近臂向下带、尚未触桌；058–060细烟从新真药头`(1333.5355768960655,827.4023133073218)`生出并向上弯动，无旧位悬空残烟。芯火持续独立燃烧，火柴无复燃。单纸盒、薄底影、远单镯手与低灯杆保持，[作者实看记录](author_actual_review.json)。

[验证](verification.json)：61源PNG逐帧对实际视频解码，最大RGB MSE `9.91068649`；[ffprobe](ffprobe.json)确认61帧单视频流。静态辅助232个旧子样、51旧层原字节、原光/火/烟ctx回归通过，未替代实际图像审查。首次预检只因稀疏检出未落盘共享留言而停，0Canvas；补齐只读检出后71/71全核过，详情`preflight_note.json`。

实际渲染严格用原命令，只加系统Chromium选择及只读网络记录：

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first61/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0207_s08_first61_scene/s08_first61_scene.js build/S08_first61_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 2.4166666666666665 --to 2.5416666666666665
```

[原日志](increment_command.log)、[实际网络日志](actual_network_events.jsonl)、[摘要](actual_network_summary.json)保留：058三层在两页共6响应均200，0pageerror/0requestfailed。实际favicon404 console位置照录，未声称全部请求200。成功加载文件逐一核固定Git原字节。

独立私有分支`cloud/s08-first61-render-20261019`基于固定源，只交本目录；不改共享实现/留言/ready/EDL/声音，不推共享主分支。S12输入包保持原字节，下一项才按单次授权生成018。
