# S22背景四推时间修正：仅一行曲线，120帧已重渲

按Astra实审，将本镜`turtleStep`唯一一行从`sstep(1.4+k,1.72+k,t)`改为`sstep(1.5+k,1.82+k,t)`。持续时间仍0.32秒，四次均延后0.1秒；`turtlePose(t)`及原`walk`判定、材色、相机和场景光保持原字节。

| 推动 | 旧背景区间/s | 新背景区间/s | 人物起帧 |
|---|---|---|---|
| 1 | 1.40–1.72 | 1.50–1.82 | 036 |
| 2 | 2.40–2.72 | 2.50–2.82 | 060 |
| 3 | 3.40–3.72 | 3.50–3.82 | 084 |
| 4 | 4.40–4.72 | 4.50–4.82 | 108 |

[新实际120帧实景MP4](../scene120/S22_actual_scene120.mp4)：1920×1080、24fps、120f、5秒，无音轨。唯一视频SHA：`2370ae5b951a98e22ab1ece6ab082f4c0489850e0f614a43a59728f2b01378d2`；新模块SHA：`a5d4596d86e9e8a485b70ad3f567716ee6878637f96236b4003a59c42d659d1f`。基线`3be9bc37c392fed5cea38e566a47a8195ff27bdc`的旧实景SHA为`d939665e2e618fb9613253b374ce4f43bd60541d4736b65c1b7365d72aec4af0`，旧片仍可从该提交读取，必要小清单及旧源代码保存在[provenance/](provenance/)。

[四组三帧实际全景总览](qa/actual_four_push_triplets.jpg)。以下均直接从新MP4解码，保留完整1920×1080原图：

- 第一推：[035](decoded_actual/F035.png) / [036](decoded_actual/F036.png) / [037](decoded_actual/F037.png)；[旧/新乌龟局部](qa/push_F036_before_after.jpg)。
- 第二推：[059](decoded_actual/F059.png) / [060](decoded_actual/F060.png) / [061](decoded_actual/F061.png)；[旧/新乌龟局部](qa/push_F060_before_after.jpg)。
- 第三推：[083](decoded_actual/F083.png) / [084](decoded_actual/F084.png) / [085](decoded_actual/F085.png)；[旧/新乌龟局部](qa/push_F084_before_after.jpg)。
- 第四推：[107](decoded_actual/F107.png) / [108](decoded_actual/F108.png) / [109](decoded_actual/F109.png)；[旧/新乌龟局部](qa/push_F108_before_after.jpg)。

[逐帧时间对照CSV](timing_comparison.csv)：每组推前一帧旧累计步值为`k+0.0875755593`，新值为`k`；起帧新值为`k`，后一帧为`k+0.0464474713`（k=0/1/2/3）。这对应曲线在起帧起步，下一采样帧进入推进，人物在起帧换到已锁新态。旧F35迈腿早于人物首推的问题按指定曲线修正。

[实际验证记录](provenance/timing_checks.json)：12张人物源图SHA、资源映射JSON/JS、120行曝光CSV及尾态锁文件均与基线逐字节一致。只有34–43、58–67、82–91、106–115共40张原Canvas帧变化，其余80张逐字节不变；所有变化均在四个曲线影响窗口内。实际新片120帧回解通过，资源失败0；[全片原帧/HTTP/ffprobe清单](../provenance/actual_scene120_manifest.json)、[120帧独立回解检查](../provenance/actual_scene120_checks.json)、[实际看图记录](provenance/author_visual_review.json)齐。

复现：[check_timing.py](check_timing.py)会从基线Git对象恢复旧片、核唯一曲线变化与锁定文件SHA，并从新旧实际MP4重新抽取指定12帧；不依赖旧临时文件。新片渲染仍用原[正式Canvas捕获脚本](../render_scene120.cjs)。

本轮图像生成0，12人物图、原曝光、材色与接触均未改；共享EDL/audio/ready及生产主分支未动。仅交本镜时间修正候选，**整镜仍不能ready，待Astra继续实审**。
