# S10 新色 v2 实际增量核验

固定提交：40aca5fa89d07d017e41d69cbe48ff1e18a3ca79

结论：S10_drawn_v2.mp4 已接入指定新色 4f178f2c 源，H.264 逐字节相同。实际解码 120 帧、24 fps、1280×720；视频/音轨呈现长度均 5 秒，起点均 0。交付 MP4 和 PCM 哈希均与更新清单相符。

S10_pcm.wav 与已核 a039936 新母带交付 PCM 文件逐字节相同；对独立重建母带的切片最大差 3 LSB、RMSE 0.006922187 LSB。audio 全套源码与 EDL 均未变，无需重建母带。

新 AAC 对 PCM 最佳延迟 0 样本，相关系数 0.998796342，真峰 -4.51 dBTP。PCM 为 48 kHz 双声道、240000 样本；AAC 解码 240640 样本，初始 1024 样本 priming 有标记，尾部 640 样本属 AAC 块补齐，不计入 5 秒呈现长度。AAC 有损，不称 PCM 逐字节相同。

MP4 SHA256：32df59b1939dfad7eedbb03a5c15b0c92a5437af696e3905fa31d11e374d8beb
PCM SHA256：8e7ed552c7d6fe9a8bd76bc0269f0acaf9e208b56ea37a1fffe0104952aeaf16
新色无声源 SHA256：4f178f2c1d8486303e26f8db1ffaf04f68c1b52b59f22d73d039bf303fd494d4
独立新母带 SHA256：d7077bb6eb8c1fd6f80d6af99e5d5c2314b7ae8724054e0ab603631563121346

仅关闭 S10 新色 v2 的画面来源与新声增量。未重核其余七镜、未重渲影片、未重建母带、未写仓库。旧 v1 在此提交删除属于版本替换，固定历史仍可读取。

机器结果：incremental_check.json。重放：python3 verify_s10_v2.py。
