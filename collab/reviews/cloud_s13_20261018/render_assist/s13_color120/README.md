# S13语义修色版 · 真实120帧复验

固定源提交`06a588dfbcb0124dfeaee563bcde07613f6bf5f6`。按指定原`frames.cjs`命令实际渲染`/js/anim/s13_drawn.js`：[实际MP4](S13_color120_720p24.mp4)，1280×720、24fps、120帧、5秒、无声。源入口为`collab/reviews/20261018_1712_s13_semantic_color/README.md`。本包不改色、不生图、不登记ready；整合与原速主观终审交Astra。

已实看[全部指定节点](00_all_requested_decoded.jpg)、[前8态人物近图](01_portraits_000_050_actual.jpg)、[后8态及119近图](02_portraits_058_119_actual.jpg)、[实际眼口2倍裁近](03_eyes_mouth_actual_2x.jpg)、[84闭口/87转头/尾态细序列](04_close84_turn87_settle_actual.jpg)及[全120帧解码次序](05_all120_decoded_order.jpg)。肤色保持暖肤，头发保持深棕，裙子保持柔黄，未见此前逐张变白、发尾变浅棕、裙子增艳的累计趋势；转向后的脸略暗，原灯光与方向保持。眼白、上睑灰影、虹膜高光及口部细节仍可辨，未出现抹平保护区的色块。

F078/083口仍微开，F084–086口缝完整闭合；F087–089整头转向正面，090/094继续转开；100进入最后一张，持至119。嘴先闭、头后转的原曝光保留。原后段外张发尾与呆毛形状仍在，本轮只复验修色，不把旧几何观察说成已修。

`decoded/`保留F000/018/024/030/036/040/044/050/058/068/078/084/087/090/094/100/119共17张原尺寸实际解码PNG。接触表与裁近图均从本次MP4解码取得，只缩放/排版，不重画。720p真实Canvas源120张保留在工作区`build/s13_color120/`，未放入审查包；逐帧源SHA在[编码核验](actual120_validation.json)，120帧顺序全部对应，最大RGB通道MSE为9.112。帧数/尺寸/时长/无音轨由[ffprobe](ffprobe.json)确认。

[独立源核验](source_validation.json)直接读取固定提交父版原PNG、当前16张生产PNG及上游复现包mask，重新核实16/16采用SHA；F000/F018和模块原字节不变，alpha、深线、有效mask外及保护五官变化像素均为0。未重新生产或编码任何人物素材。区域均色最大通道差0.4959来自上游FROZEN的材质域统计；不把该数值当作动态场景灯光下像素均色±4的承诺。

[浏览器实载记录](browser_resources.json)逐个对实际HTTP图像、背景、字体及JS做浏览器SHA256，并核对本地和固定Git blob；16态入口与全120帧模块选张一致，页面错误0。原favicon404不影响必需资源。资源补查最初把有效同源`//js/...`路径误作协议相对地址，诊断日志保留于`browser_check_initial.log`与`browser_check_path_diagnosis.log`；仅修本包QA取址，最终[补查日志](browser_check.log)通过，未改场景。

[原命令/环境](run_manifest.json)、[渲染短日志](render.log)、[解码短日志](decode_check.log)与`tools/`可复核。原shim只指定系统Chromium，不改变源模块、公共渲染器、相机、素材、EDL或音轨。本次image-generation调用0，ready写入0；完整声音和最终接片不在本轮范围。
