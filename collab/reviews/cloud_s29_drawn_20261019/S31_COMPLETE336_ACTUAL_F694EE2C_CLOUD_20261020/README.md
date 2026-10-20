# S31 原始完整336帧实际交付

固定来源 `f694ee2c3b36aa21c1476faa7268a96148f820f4`，原包 `collab/reviews/20261020_0031_s31_complete336_gate`。原 PID **11232** 唯一一次执行已完成，`EXECUTION_LOG.json` 为 **passed / 336 of 336**；没有重启、替代任务、额外场景渲染或新生成。

交付 `S31_COMPLETE_336_VIDEO_ONLY.mp4`：**1920×1080、24fps、336帧、14秒、H264/yuv420p、静音**，7,083,617 bytes。SHA256 **`c9ec246b09b4ed01aaa25fe3d51ea47e3e0926601592620e975a97a951af99e9`**。本文件和六张原始 PNG 均为 `/tmp/s31_complete_336_actual/` 原输出的逐字节副本，没有转码或重录。

实际核验：

- 原运行的40项运行时 SHA 及42项完整包文件在运行前后全部一致；源码/素材未改。
- 原日志无页面错误、失败请求或必需资源 HTTP 错误；六张原 PNG 为 F000/036/116/179/180/335，没有输出336张散帧。
- 独立 `ffprobe -count_frames` 核实336帧和14秒；`ffmpeg -xerror` 完整解码336帧，stderr为空，PTS 0–335、全部YUV尺寸正确。逐帧摘要见 `ACTUAL336_DECODED_YUV420_FRAMEHASH.txt`。
- 浏览器把同一 MP4 实际播至 `ended`：336 total / 0 dropped / 0 corrupted，无媒体、页面或请求错误。见 `ACTUAL_COMPLETE_MP4_BROWSER_PLAYBACK.json`。
- **A→B F180 与独立原始 B 的第二次绘制 RGBA 零差**：0 changed channels / max0 / total0；两者摘要均 `b717fe249e862749df50ff06ee8b3e9d7942fd7785254aaf55d190bc923ca961`。独立 B 控制页没有运行 A，完整序列使用另一个新页面，没有预跑 B。
- 独立 B 首次与第二次绘制自身为 **21 channels / max1 / total21**；原始记录完整保留，不称该对照自身零差，也未放宽 F180 的硬性零差门。

实际看图入口：`SIX_ORIGINAL_PNG_CONTACT.png`、`ACTUAL_MP4_28_SAMPLES_CONTACT.png`，原尺末帧为 `F335.png`。作者已实际打开六张原 PNG 和全段28抽样；独审补看末335与两张接触表。前景持龟拳的两根真杆保持入掌，抬臂各抽样未见新增断接；另一手握灯，暖灯关系稳定。179→180 切回原始 B，B 段鹤龟至335未见新增结构故障。奶奶半开包的轮廓、双手支持与暗开口在已批准暖光/14px虚化下可读；细鹤红头、颈及杆在背景中不能可靠细辨，保留此观察，不另立导演门。

视觉范围为六张原 PNG 与28张编码抽样，**没有把完整解码或浏览器播放写成逐帧视觉全审**。此包供 Astra 统一整合和主审；未改 ready、声音、EDL 或生产实现，不自行宣称整镜 ready。

`ORIGINAL_LAUNCH_RECEIPT.json`、`ORIGINAL_RUN_STDOUT.log`、`READ_ONLY_RUN_OBSERVATIONS.jsonl` 保留原次运行来源与持续观察；`EXECUTION_LOG.json` 是原日志副本。`COMPLETE_ACTUAL_RUN_VERIFICATION.json` 汇集独立数值核验。`verify_and_copy_original_complete_run.py` 仅核验/复制既有成片，拒绝覆盖；`check_original_complete_video_playback.cjs` 仅播放成片，两者均不调用场景渲染。
