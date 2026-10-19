# S08 first96｜修复薄影后的实际96f候选

固定源 `e011da850ced918ee5d4587afbdd92a349d6929d`，95路径渲前／渲后核Git原字节；入口 `collab/reviews/20261019_0421_s08_first96_scene/s08_first96_candidate.js` SHA `1a91cac4dab14340bd0edfd24ce71102666144f613dcf254b635cbc1cf5e7535`。

- [96f/4秒/1080p24静音片](S08_first96_1920x1080_24fps.mp4)，SHA `ef7aad0f2e8043765d0448dbde60aac02bd24fd8507cafd28f3c5a22b7559f03`。
- [21张最终新增Canvas](canvas_new/)：075–077保留原3a33首次结果，078–095为e011补影结果；旧000–074逐SHA及字节复用固定 `5f25589722c5dfa4b1e5f97fdfb6d392ee10d107`，未重渲。
- [15帧实际解码](00_actual_selected15.jpg)、[077→078松手／080→081罩杆回位](01_release_return_actual1_5x.jpg)、[后坐双手／单盒／固定柴](02_retreat_hands_box_match_actual2x.jpg)、[旧新桌柴薄影实际4倍](03_old_new_match_shadow_actual4x.png)。完整关键解码PNG另在 `decoded/`。

已实看：078先松手，080罩随杆落，081杆归位；088/091/094完整身体后坐且双手跟随，逐渐露出唯一原盒。桌柴／烟根固定，独立芯火稳定。薄影修正18帧只改变x1222–1265/y961一行，未越981前唇；该区域外RGBA逐字节全同，[差异记录](shadow_correction_comparison.json)。

旧3a33的全部21张实渲、旧96片与日志保留在 [pre_shadow_fix_3a33/](pre_shadow_fix_3a33/)，不作当前成品。按后续明确修正只重渲078–095，075–077与旧75均未重做。两次增渲／两次版本编码，最终版本只编码一次，新生图0，096以后未渲。

[核验](verification.json)：全部96源PNG与视频逐帧解码比较，最大RGB MSE `10.409498215`。旧75的300子样合同、72旧层、绘制源及8项共用运行文件核同；最终21张可追溯到两次真实浏览器PNG。32次新16层响应均200，0pageerror/0requestfailed，真实favicon404 URL保留于 [资源摘要](actual_network_summary.json) 与原日志。

仅本独占目录，私分支 `cloud/s08-first96-render-20261019`；未改共享实现／留言／ready／EDL／声音。完整144按另行派发源接在此正确96后增渲。
