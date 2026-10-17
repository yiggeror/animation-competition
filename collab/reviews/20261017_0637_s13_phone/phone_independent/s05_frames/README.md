# 解码帧复现

本次增量包保留了覆盖全部96帧的整帧/拇指连续证据板，不重复上传可由既存MP4恢复的96张全帧PNG。审查时确实逐帧解码，源hash与命令见上级报告。

```bash
ffmpeg -i ../../../20261017_0616_integration/phone_actual24/S05_24fps_audio.mp4 -vsync 0 -start_number 0 %04d.png
```
