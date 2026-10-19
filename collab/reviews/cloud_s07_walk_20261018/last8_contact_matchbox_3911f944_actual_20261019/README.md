# S07 3911f944末8帧实际增渲与完整108帧编码

固定源：3911f944f5db4ed17625b83e06ff813d8c455b3f。仅实际渲100–107八帧；000–099逐字节复用f35f9ae2工作树原无损PNG，100张SHA全部核对。没有重新渲整108帧。3张可见F100/103/106生产PNG也已对abc2059逐字节核对不变。

实际完整成片：`S07_full108_REUSED100_NEW8_3911f944_1920x1080_24fps_ACTUAL.mp4`，1920×1080／24fps／108帧／4.5秒／无声。SHA256 `f7b5279f6b3e46460e9a063fffe1d2478717ad6951c38f47e57446dca7eec3b5`。新增8张真实PNG在new_actual_png/，逐张SHA见new8_PNG_SHA256SUMS.txt；旧100张不重复打包，完整来源和SHA在source_before_render_and_reuse100.json及actual_render8_reuse100_encode108_checks.json。

实际成片已解码099/100/102/103/105/106/107，并全部实看。完整关键帧在decoded_actual_mp4/，同尺全景和边界近图在boundary_sheets/。火柴盒在原桌位置持续、始终单灯，103闭合真握和106同一握灯小幅抬起保持。原桌灯/桌影层没有恢复。

**脚影保留主审项**：新影源已分为人物alpha-only；旧灯/桌alpha带来的最右侧投影有所减弱。但实际099→100仍可看到朝桌脚方向的影子延展，不能把本次源归属改动冒称“长条外观完全消除”。旧新实际100脚区对比及仅无损PNG差分在boundary_sheets/和qa/，请Astra判断剩余人物影的接地效果；本包不自行改生产或再渲。全镜最终通过尚不声明。

运行日志render_only8.log、browser_resources.jsonl及browser_resource_summary.json齐。75项请求/回应均200，无requestfailed/pageerror；唯一console404为favicon.ico。只用原frames.cjs的--from4.166666666666667 --to4.5范围；环境适配器只在本目录指定系统Chromium，不改生产模块。MP4只编码一次；筛帧表达式逗号转义修正后仅重跑解码，没有重复渲染或编码。

复现增渲：NODE_PATH=/opt/codex/cua_node/lib/node_modules，NODE_OPTIONS加载本目录capture_browser_resources.cjs，然后运行 `node tools/js/frames.cjs js/anim/s07_drawn.js build/S07_last8_3911f944 --fps 24 --w 1920 --h 1080 --from 4.166666666666667 --to 4.5 --workers 2`。`assemble_and_decode.py`只复用原100张、拼接新8张编码和解码；--decode-existing只重做已编码片的解码。生产js/assets/tools/dev相对固定3911f944无修改。新生图0次。

S09两桥已按最新Astra主审锁定；完整96帧模块待主协调固定提交后接实际整镜渲染。
