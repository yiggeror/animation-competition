S12完整实际画面已完成：1920×1080、24fps、192帧、8.000秒。ffprobe实际解码192帧，浏览器加载错误为0。

- [完整可播放MP4](full_actual/S12_000_191_actual.mp4)
- [105→106、109→110、后半及结尾接触表](full_actual/contact_joins_tail_end.jpg)
- [双手、有限双杆及真铰点局部](full_actual/contact_joins_detail.jpg)
- [最小完整运行记录与SHA](full_actual/runtime.json)
- [独立花衫调色候选：实际光学前后对比](colour_candidate/actual_before_after.jpg)

生产入口为 `js/anim/s12_drawn.js`，生产资源和逐帧选择表为 `assets/chars/g12/sequence.json`；运行不引用reviews模块或图片。前半22曝光行与6ea2b9f完全一致，复用原[000–105实际视频](front_actual/S12_000_105_actual.mp4)。后半采用4051f3ef4d00bd1234a2e7b8cf3524c82b262c43的 `collab/reviews/20261020_s12_full192_handoff/tail/`：106、110、120、126、144五套BG/FG逐字节迁入正式资源，7行曝光严格按[原采用表](TAIL_EXPOSURE_MANIFEST.adopted.json)。132复用110，168复用144；未新增绘图。

后半106–191仅做一次实际Chromium串行渲染，PNG逐帧直接进入ffmpeg管道。只保留8张尾段关键帧；未落整套PNG序列。再以 `-c copy` 拼接原前半，保留完整原前半文件，没有重复渲染。完整视频SHA256：`b6c3ca423a7fba353db3df9632efc26c91ae74fd8062a18d012f5f954255ab61`。

人物与道具按同一曝光保持；真实 `makeCrane/solve/pointOn/drawPuppet` 画纸偶和free→BODY/NECK3的两根有限杆。尾段BG/FG是已注册的1920×1080图，按scene原位合成，不再施加275,112/.7。沿用102的原场景底图、接地影子及箱前板，保留原S12单次线性打光、灯闪、镜头、暗角和颗粒；110以前无投影，110开始沿原投影公式将同一纸偶透光材质乘到箱盖上。实际查看了110全图、两个衔接局部、120抬起、126回落、144整头转向和191结尾。

花衫变色来自批准的未打光人物PNG：早期灰蓝，090/102逐渐变为高饱和蓝；所有曝光实际共用一次相同renderPaint，没有重复乘光或分支颜色空间处理。完整主片保留已批准原图。另交[仅F102蓝色布料的候选PNG](colour_candidate/F102_BG_blue_cloth_candidate.png)、[候选读回](colour_candidate/readback.json)及相同光学下的一帧预览。候选保持alpha逐像素一致、暗色线稿不变，不修改肢体或花纹；未应用到生产选择表。若选此色向，后续统一语义调色再由主协调决定。

该MP4是无声的完整画面验收片；仓库声音、4.6/5.0秒节拍及EDL均未改。生产入口已独立可用，未替换共享EDL的S12行。不存在缺失尾图或补帧占位；剩余取舍仅为源图花衫色差候选及主协调最终整合。

迁移证据：[尾图来源/SHA](tail_source_adoption.json)，各 `Fxxx_adopted_prop_plan.json` 为采用包原真实道具计划。工具在 `tools/`；实际尾段命令已执行并完成：`node tools/js/render_s12_stream.cjs collab/reviews/cloud_s12_20261018/formal_scene_20261020/tail_actual --first 106 --last 191`。无需为同样检查重跑。
