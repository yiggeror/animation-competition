# S08 首41帧增量实渲交付

固定源码 `29a4bca29ee90eaec1e65c2d61db59047ed8efae`，入口 `collab/reviews/20261018_2259_s08_first41_scene/s08_first41_scene.js`。入口SHA256：`aad63a57deedd721296e8d415de6860bedd4fa6927ca3633ab874c9e2f084018`。42个固定运行文件已按Git原始内容与SHA256双核对，清单见 [fixed_runtime_inputs.json](fixed_runtime_inputs.json)。没有修改入口、人物图或共享文件。

## 直接交付

- [41帧静音MP4](S08_first41_1920x1080_24fps.mp4)：1920×1080，24fps，41/24秒（ffprobe 1.708333秒），只有视频流。
- 新增原始Canvas PNG，直接随片交付：[F038](canvas_new/F038.png)、[F039](canvas_new/F039.png)、[F040](canvas_new/F040.png)。它们与本次实渲输出及合片前PNG逐字节一致；[原始PNG校验和](canvas_new/SHA256SUMS.txt)。
- [037→040实际视频解码全帧](00_actual_037_040.jpg)、[近臂/侧管/远手/单盒影局部](01_near_arm_pipe_low_grip_box.jpg)、[药头与灯芯间隙4倍局部](02_match_head_air_gap_wick_actual4x.jpg)；另附4张未标记的完整解码PNG于 `decoded/`。

000–037逐字节复用交付 `f0cd7c13fa8cbba6bf8e3b86897882e04d7173cc` / 原始036–037补交 `b0477742efc63acc08ea16026b968643b484ab04` 对应的38帧缓存。复用前后均核SHA，见 [reused38_baseline.json](reused38_baseline.json)。本次仅一次实渲038–040、一次41帧编码；没有重渲前38帧，没有扩到041。旧38张PNG未重复上传。

## 实际画面与独立证据

已实际查看原始F038及037/038/039/040的MP4解码全帧和局部。近臂、手及木杆在红色侧管之前形成遮挡；药头可见真火，火根对应固定入口(1390,788)。药头右缘与灯芯仍有空气间隙；灯芯受火柴光照亮但未见灯芯火焰。远手低杆握点保持，桌面为单盒及薄影。见 [实际画面复核记录](author_actual_review.json)。本地接触复核通过，整段原速观感与冻结仍由Astra审查。

源码辅助核对单列于 [source_contract_check.json](source_contract_check.json)：旧38帧152个子采样状态一致，F038保持3帧，F041拒绝进入，wick=0、low lever lift=1。原层核对：火柴盒1665个可见像素及alpha与F036一致，盒底y=970；按像素中心计算的148像素低杆圆盘RGBA与F036一致。此类源码/图层核对不代替实际成片判断。

41帧均从交付MP4解码并逐帧对照各自源PNG，最大RGB MSE为9.45454216003418；帧数、尺寸、帧率、时长及无音轨已核，详见 [verification.json](verification.json) 与 [ffprobe.json](ffprobe.json)。MP4 SHA256：`e194d12425b0f1ea1c8dcaf1d8548bbc8a6429e6898a23c38f3740c9f85bfb64`。

## 实渲命令与范围

```sh
NODE_OPTIONS='--require /tmp/s08_first27_system_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261018_2259_s08_first41_scene/s08_first41_scene.js build/S08_first41_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.5833333333333333 --to 1.7083333333333333
```

临时shim仅将Playwright Chromium启动路径指定为 `/usr/bin/chromium`，未改绘制逻辑。原始控制台输出见 [increment_command.log](increment_command.log)：3帧完成；一条未标明URL的404保留，无观察到的pageerror，不推断为favicon，也不据此声称全请求成功。零生图调用；未启动全片、旧Blender、付费服务/API；未改S12、S24、EDL、音频或ready标记。
