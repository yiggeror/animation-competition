# S29 066–089 固定实际审片包：078/084肩袖通过；072残缝HOLD

本轮0次生图。原078完整肩袖语义片只按既有078整臂矩阵接回，078与084共用完全相同的源片及矩阵。实际看过正常全图、完整袖口和实景解码；本轮修复的两态外轮廓连续，缺齿、白阶及灰V消失。原alpha、白花、黑外轮廓保留，未描线、未拉袖；两态手腕以下RGBA逐像素不变，布、双手接触、单镯、真偶及四杆沿用上一锁态。

**整体仍HOLD：本轮原字节保留的072候选，在实际072–077帧远袖口与上臂之间有细透背景斜缝，外端有肤色尖角。** 实际1920×1080坐标约x795–875/y500–560；071→072出现，077→078消失。主代理与现有6.1sol均已实看确认。072需同raw完整袖口接回后再验证该六帧；本轮不超出限定18帧渲染另开重渲，不冒称24帧视觉全过或整镜ready。

- [实际24帧静音片](S29_F066_F089_REUSED6_NEW18_ACTUAL_1080p24_SILENT.mp4)：066×6→072×6→078×6→084×6，1920×1080、24fps、1秒、无音轨。
- [三处换态实际袖缘1:1](THREE_SWITCHES_COMPLETE_FAR_SLEEVE_ACTUAL_1TO1.png)、[完整双臂换态1:1](THREE_SWITCHES_COMPLETE_ARMS_CONTACTS_ACTUAL_1TO1.png)、[实际24帧接触表](ALL24_REUSED6_NEW18_ACTUAL_DECODED_CONTACT.png)。解码图按原亮度审查。
- [实际新渲18帧片](S29_F072_F089_NEW18_ACTUAL_SCENE_1080p24.mp4)：只调用072–089各一次；066–071六帧直接复用历史片解码YUV，无浏览器重绘。最终无损H264封装，全部24帧独立解码YUV/RGB均与对应旧6或新18样本完全相同。
- [最终078 RGBA](F078_FINAL_RGBA.png)、[最终084 RGBA](F084_FINAL_RGBA.png)；[完整原078源片](ORIGINAL078_COMPLETE_SHOULDER_SLEEVE_CUFF_PROXIMAL_ARM_RGBA.png)、源/目标语义域PNG及[同矩阵检查](COMPLETE_SLEEVE_SAME_RAW_SOURCE_CHECK.json)。072与066均原字节保留。
- [实际渲染日志](ACTUAL_BROWSER_RUN.json)、[逐帧解码账本](REUSED6_NEW18_ACTUAL_DECODE_CHECK.json)、[浏览器完整播放检查](FINAL24_ACTUAL_BROWSER_PLAYBACK_CHECK.json)、[实图审查结论](ACTUAL_VISUAL_REVIEW.json)。Chromium实际播放24帧，0掉帧、0损坏、无媒体错误。第一次仅播放器验证遇静态服务器MP4 MIME，改为同字节video/mp4后通过，未增加场景渲染。
- [全部原始来源/实际请求/完整prompt入口及SHA](ORIGINAL_CALL_SOURCE_INDEX.json)：既有三次生图及完整原件都留在上一固定包，本轮仅索引，不改历史。各态原始请求均有完整五张实交参考、逐字提示词和原始工具返回。

实际代码只借机位、灯光、场景及原时长；人物来自画稿。场景四项生产源SHA渲染前后相同。仅本独占review目录有新增，未改生产、024/030、Opus实现/留言、共享文档、ready、音频或EDL；未渲整镜。

复现脚本分为 `restore_complete_source_sleeve.py`、`render_new_eighteen_only.cjs`、`assemble_reused6_new18_and_decode.py`、`check_final_video_browser.cjs`。本交付已实际运行一轮18帧，请勿对固定成片覆盖重跑。为缩小交付仅保留新画稿态072/078/084的原Canvas和066/071/072/077/078/083/084/089八张实际解码PNG；所有18个Canvas及24个解码帧SHA完整保留在账本中。
