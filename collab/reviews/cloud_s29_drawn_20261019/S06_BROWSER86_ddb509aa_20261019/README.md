# S06 正式 Chromium 86帧实际验证

固定生产源 `ddb509aa7e8283134e76980a638c81155578f520`，独立fresh浏览器仅渲一次完整86帧，原脚本SHA `7aff911d4b25d4151ed3ad64a2ce6cce8690e562ba02c4e3404010217d9a05e3` 未改。实际片 `S06.mp4`，SHA256 `f19c654be13b3d8ef97fefb135ef6522a577466eb30e7ed5cb30d673524bc3ba`；1920×1080/24fps/86f/3.583333s/无音轨，进程76239退出0。

本机缺Playwright默认缓存浏览器，审查目录runtime_observe.cjs仅选择已安装 `/usr/bin/chromium` 并观察HTTP/退出；生产模块、7原图、原流式脚本/Canvas默认属性均未改。11个移交文件及shared paint/bg/dev/serve逐字节对ddb509aa核过。7角色PNG+背景8资源均200；13个已捕获response均200，页面异常/请求失败0。实际还记录一条URL未捕获的console404及原脚本Socket MaxListenersExceededWarning，原文保留在render_actual.log，不冒称无错误日志。

只保原Canvas F000/F085两张，PNG直接流给ffmpeg；没有全PNG序列或CPU场景重渲。独立MP4全解码86帧RGB24 SHA见FULL86_DECODED_RGB24_FRAME_SHA256.txt，指定12张回解图在decoded/。CONTACT_BEFORE_AFTER_PAIRS.jpg、EYES_034_039_078_085.jpg、CUT_S06_085_TO_NEW_S07_000.jpg已实际打开。

四组10/11、29/30、45/46、69/70接点前后可读；34/39和78/85是既定phone-glance曝光保持。新S07切点来自已通过full108的4403cb10 MP4，视频SHA与原交付一致，独立回解F000。需主审留意：S06F085仍握充电器，S07F000已双手持手机，切口省略了松插头/收手动作；本验证不改生产去补这一动作。完整时序观影及切口/声音决定仍归主协调。

ACTUAL_VERIFICATION.json、FFPROBE_INDEPENDENT.json、FROZEN_SOURCE_AND_SCRIPT_CHECK.json和RUNTIME_HTTP_AND_EXIT.json为实际检查记录。一次跨文件系统rename归档失败已改为复制续归档，复用既有解码结果；未重渲。EDL/音轨/生产资产未改。
