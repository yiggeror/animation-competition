完整MP4原字节分为两段，仅为GitHub连接器单请求大小限制，不是重新编码。

在本目录运行：

    cat workprint.mp4.part1 workprint.mp4.part2 > workprint_360p24_silent.mp4

SHA256: 0b19a165682a060be632469680a051bad728eb49c0a14bb468a7a7709c7e3c59

13,377,583 bytes；5235帧；640×360；24fps；218.125秒；静音画面工作片，非高清音画终版。

Windows/macOS/Linux 通用方式：安装已有 Python 3 后，在任意目录执行 `python restore_preview.py`（脚本路径按实际位置填写）；脚本拼接后核对字节数与完整 SHA256，失败不会写出文件，不进行任何视频编码。
