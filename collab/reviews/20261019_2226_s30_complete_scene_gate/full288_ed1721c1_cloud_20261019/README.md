# S30固定ed1721c1：唯一一次全288帧实际渲染

结果为HOLD：原脚本已完成全部288帧编码，随后重复诊断120、190各自JPEG哈希一致，第3次诊断0帧哈希不一致，原脚本以ERROR/退出码1结束，末两次190、120没有执行。保留原失败报告，不改成通过、不重跑。失败重复0的JPEG本身未被原脚本保存，当前只有哈希证据，不能宣称知道其具体视觉差异或原因。

授权来源：Astra已实际审阅20张静态关键帧，追加允许沿固定`ed1721c17b4e27d1e72a4379cdd67eb3edfeef21`运行一次原脚本`--all`。本包保存该次完整12秒静音MP4、原脚本的20张JPEG、完整报告及有限回解证据；没有再次单独运行20关键帧门，没有新增生图或重传22张原始人物PNG。

执行命令（已执行，勿当作待执行步骤）：

```sh
NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node collab/reviews/20261019_2226_s30_complete_scene_gate/render_repository_keyframes.cjs --all
```

原脚本SHA256 `ee1be7b737925a68cbb5b252e9ad9282b681580b9ce6ecc50da97f0cfcc9931f`，人物模块SHA256 `edfdd2cb5e4ae95f639bab6ef58bd2253918e4a3b746a11065336a2d067170d4`。执行目录为独立固定源码副本`/workspace/s30-full288-ed1721c1-20261019`，生产分支、EDL、声音、公共helper均未改。

## 文件

- `actual_browser_frames/S30_COMPLETE_288f_24fps_NO_AUDIO.mp4`：原脚本流式编码完整镜头。
- `actual_browser_frames/F*.jpg`：原脚本20张Canvas JPEG(.96)关键帧；不是PNG或RGBA零差门。
- `actual_browser_frames/ACTUAL_BROWSER_RENDER_REPORT.json`：288次正式绘制状态、22原件SHA、资源/浏览器错误、实际执行的3次JPEG重复诊断。诊断帧不追加到视频。
- `CLOUD_FULL_RUN_AUTHORITY.json`、`CLOUD_FULL_RUN_STDOUT.log`：唯一一次启动与原stdout。
- `FFPROBE_FULL288.json`、`CLOUD_FULL288_VERIFICATION.json`：帧数/帧率/静音、288帧独立回解SHA、全帧状态转换及31项受保护源码/资源的事后SHA。
- `decoded_review/ALL_FRAMES_SECOND_00..11.jpg`：按时间顺序覆盖实际MP4全部288帧的12张联系表，每张24帧。
- `decoded_review/DECODED_F*.jpg`：10张实际MP4独立回解的有限全尺寸关键JPEG。
- `ACTUAL_FULL_SEQUENCE_VISUAL_REVIEW.json`：主审及现有只读云审的实际逐帧/换态查看结论及限制。

回解使用`decode_full_run.py`流式读取已有视频，每次仅一帧RGB；不落全PNG序列、不调用浏览器渲染器。渲染器只保存原定20张JPEG；回解另保存12张顺序联系表和10张有限关键JPEG。

当前完整视觉结论见`ACTUAL_FULL_SEQUENCE_VISUAL_REVIEW.json`。本包交Astra复核后统一整合，不登记ready，不预称Opus配声或EDL已完成。

渲染中遇到工作区满盘：Python缓存目录创建失败后，移除一个干净、无进程占用的旧临时渲染工作树，恢复3.2GiB。渲染器从未重启，原脚本未记录ffmpeg写盘错误；完整视频另做全部288帧流式回解。详见`DISK_RECOVERY_INCIDENT.json`。此记录不证明重复0失败与磁盘或GPU有关；当前没有足够证据归因。

实测视频SHA256 `59714a0358815004098244c80ff982e6807ec5c31aea1d41aae1b60b091c2760`，288帧/1920×1080/24fps/12秒/静音全部回解成功。主审和现有只读云审均实际打开12张顺序表与10张完整解码帧，按键→走步→够握拉绳→144灭灯→147松指→190原头影的因果可读；这是解码序列与完整静帧审，不声称实时播放或完整动态美术终审。隔离HOLD不被肉眼结论覆盖。

与前次静态门20张既有JPEG比较，9张字节相同；11张解码JPEG RGB平均通道差0.36–0.42、最大6–9。这不是原CanvasRGBA比较，也没有失败重复0原图，不能据此给失败原因或判其无影响。
