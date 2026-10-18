# 当前交付：93705f2修后静止咬合版

本独立入口已只改一行，读取 `sheet23(5, env)`；实际运行必须搭配93705f2修后的共享S23。新60帧MP4、S23末→S24首真实切换解码、九图SHA未变证据见 [bite_fix_93705f2/README.md](bite_fix_93705f2/README.md)。作者实际咬合与跨镜接续核对通过，待Astra最终整合。以下保留155d259原片及问题记录，供历史对照；新交付以本段链接为准。

---

# S24完整60帧正式场景候选 · 待Astra整景门

[实际场景MP4](actual_scene/S24_scene60_1920x1080_24fps.mp4)：**1920×1080 /24fps /60帧 /2.5秒 /无音频**，SHA `40a2f7c38a9f53167b381babc73b9b286701ccda530b18c811c22dd7dc90bf19`。真实Chromium完整渲染，非灰深底人物层。已实看九态和切换关键解码，人物接景、资源与编码门通过；有一项幕上咬合问题待Astra原速整景终审；未登记ready。

先看[九态实际场景接触表](actual_scene/00_all9_actual_scene_decodes.jpg)、[各曝光切换前后帧](actual_scene/01_all_exposure_boundaries_actual_decodes.jpg)、[024→032→040及末停](actual_scene/02_peak_settle_hold_actual_face_neck_tails.jpg)、[袖边场景细节](actual_scene/03_actual_sleeve_edges_scene.jpg)。18张完整1080p实际MP4解码PNG在[decoded_keyframes](actual_scene/decoded_keyframes/)，包括000/005/006/008/009/011/012/014/015/018/019/023/024/031/032/039/040/059。

[独立入口](s24_drawn.js)与25ae2c72的入口逐字节相同，仅[锁记录](final_lock.json)按本轮Astra明确双审登记批准。唯一九张图沿79840218；032=cd01c1cc…e3e43、040=724d5c1c…16b8，所有PNG及此前完整人物层包逐字节不变。[60帧资源映射](resource_map_60f.csv)为6/3/3/3/4/5/8/8/20，B=.70+(590,20)，没有翻转、旋转、拉形、插帧或代码人物。源图、原件/prompt与局部材质校准保全仍见[人物层锁包](../d08_d09_final_segment/README.md)。

实际画面中，眼先动→整头连颈肩回看→闭口小笑微抬颏→032轻回落、尾内收→040落定均读得出。头顶净空，领颈与袖根连续；人物按原场景暖光受光，未以场景效果改写锁图固有色。040原生右缘y1255/1256两个黑描线切点保留，绝不宣称透明余量。[作者实看记录](qa/AUTHOR_ACTUAL_SCENE_REVIEW.json)列明范围；最终原速节奏与整景门交Astra。

**整景待处理项：**沿用的`sheet23(3.4+.1*t)`在实际059中让鹤嘴尖与龟头/嘴区出现可见间隔，未保持“咬住”的接触。[000/040/059实际裁区](actual_scene/04_inherited_puppet_contact_review.jpg)与[观察记录](qa/inherited_puppet_contact_observation.json)明确保留。该问题来自本轮逐字节保留的场景路径；本轮人物门通过，不签幕上咬合或整景ready。交Astra裁定接景修正，未擅改已批入口/既有皮影机构或重复渲染。

沿固定c9208575场景：世界相机pos[3.15,1.62,1.12]/target[1.80,.62,.98]/hfov46、曝光.22、雾.5、sheet23(3.4+.1*t)、房间/幕/龟鹤及原灯光。19项场景JS及5项工具/预览页/字体源均与固定提交一致，未改共享渲染器。普通漫反射平面卡片的固有色是原生真实画稿。040–059同一锁图，场景灯闪/雾/颗粒继续，所以场景PNG不冒称逐字节相同。

[逐帧与资源验证](qa/actual_scene_validation.json)：60帧Canvas源与60解码一一对应、逐帧资源态/SHA/PNG SHA核对，最大编码MSE **8.80473**；[ffprobe](qa/actual_scene_ffprobe.json)独验时长/帧数/尺寸/无音频。实际浏览器九张PNG网络成功读取共18次，均HTTP200且SHA与锁图相同；入口、锁JSON及实际场景JS响应也核SHA。0 pageerror、0 requestfailed、0审计错误。控制台有1条未带URL的404，关键资源完整加载；不推断未知URL为favicon。[完整浏览器事件](qa/actual_browser_events.jsonl)与[命令日志](qa/actual_frames_command.log)保留。

首启动因稀疏工作区缺两个已跟踪字体，预览页字体等待失败，产出0帧；补齐原仓库同SHA字体后一次成功渲完60帧并编码1次。失败日志和根因保留在[failed_attempt01_fonts](qa/failed_attempt01_fonts/)，不把失败抹成首次成功。WebGL2/浮点缓冲已实际可用，进程级系统Chromium+SwiftShader配置只在[审计shim](tools/actual_chromium_audit_shim.cjs)，没有更改生产源。

复核命令：`python collab/reviews/cloud_s24_20261018/scene_candidate/tools/check_actual_scene.py`。需要保留本工作区build/S24_scene60的60张原Canvas PNG、build中的原MP4；它们未清理。渲染命令、入口/锁SHA见[请求记录](qa/scene_render_request.json)，锁定授权见[来源](provenance/astra_final_tail_lock_and_scene60_authorization.md)。本轮生图0；未启动全片、Blender、新付费服务或API；未改音轨、EDL、共享生产主分支或ready。
