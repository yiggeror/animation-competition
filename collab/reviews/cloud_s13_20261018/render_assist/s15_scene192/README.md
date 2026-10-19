# S15 整镜实际候选｜192f / 8秒 / 1080p24 无声

固定源 `5271da8b1870bf4523cd7bb4eaf101f77147d6d8`，24路径渲前与渲后均核对Git原字节；入口 `collab/reviews/20261019_0434_s15_drawn_candidate/s15_drawn.js` SHA `f3b6439da5e152961dce1c81bb615b86bc0a8ef06e3d8c37d52cab0d339360f0`。8张画稿及整人物16.5px/cm注册、F144整层0.94、原仰拍相机／灯／幕均未改。原坐点在画外，左前景鞋凳裁切已由主审接受；[继续整镜的明确指示](full_scene_authorization.txt) 保全，早先三帧检查仅留历史记录。

- [8秒实际静音片](S15_scene192_1920x1080_24fps.mp4)：192帧、1920×1080、24fps、单视频流。SHA `c0e2a0cd0ba9ebd6ed1f6829df558f4e452e680a33007126f9c57e492e76ffac`。
- [实际全景关键解码](00_actual_scene_keyframes.jpg)、[未提亮的脸／解臂／前倾原像素近图](01_actual_face_arms_progression.png)。完整关键解码PNG在 [decoded/](decoded/)，包含108／112／116／120／124／132／144，以及000／072／191。
- [逐帧验证](verification.json)：全部192源Canvas与实际视频逐帧解码比较，最大RGB MSE `8.841352463`；浏览器直接PNG的192个SHA均匹配实际源文件。三张预检000／132／144与整片同帧Canvas也逐字节一致。

已实看实际解码：鹤影从大虚收为清楚幕影；108起交臂逐步打开，120/124双手落膝，132→144整头颈肩躯干一起前倾，视线朝鹤。动作在原光下可辨；眼鼻嘴仍在低照度蓝色暗部，附原像素近图供终审，没有用提亮图替代实际画面。[实看记录](author_actual_review.json) 为作者候选检查，待Astra最终整合审查。

本次完整192只渲／编码各一次，另有已交的3张预检；本次新生图0。保留全部原Canvas与完整解码于本地 `build/S15_scene192`／`build/S15_scene192_decoded`，不上传重复源工程。交付视频是原编码文件的逐字节副本。

[实际资源原日志](actual_network_events.jsonl)、[摘要](actual_network_summary.json) 及 [固定24路径](fixed24_readback.json) 齐全。8张本地画稿的响应均200，成功运行文件28项与固定Git原字节一致，0pageerror／0requestfailed。实际console404 URL原样保留：`http://127.0.0.1:37695/favicon.ico`。

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s15_scene192/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0434_s15_drawn_candidate/s15_drawn.js build/S15_scene192 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S15_scene192.mp4
```

仅本独占目录交付至私分支 `cloud/s15-actual-render-20261019`；未改共享实现／留言／ready／EDL／声音，未推共享主分支。
