# S28 全 192 帧实渲门

目标目录 `collab/reviews/20261019_0930_s28_full192_actual/`。原云串行执行，只调用已锁 `8a86a552` 的 float `entry_full192.mjs`；不改图、光、机位、音轨。帧 000–131 为舞台，132–191 为已批手机末插。

```sh
python3 -m http.server 8197 --bind 127.0.0.1 >/tmp/s28-full192-http.log 2>&1 &
S28_HTTP_PID=$!
S28_OUTPUT_DIR=/tmp/s28-full192 node collab/reviews/20261019_0930_s28_full192_actual/render_full192.cjs
S28_STATUS=$?
kill "$S28_HTTP_PID"
exit "$S28_STATUS"
```

每 24 帧输出进度，每张原始 PNG 的 SHA 写 `FRAME_SHA256.jsonl`。PNG 顺序直送 ffmpeg，不落地完整大序列；留 11 张关键图、8 秒 24fps MP4 和 `FULL192_CHECK.json`。预计舞台约 55 分钟；原云可保全输出，只回最短可审视频/报告与必要切点图。此视频无音轨，既定 .2/1.4/5.5 秒声点未修改，音画合成另用原制作音轨。静态六图已实际通过，完整动作及 131→132 切点仍待整段实看。

不能按同姿 PNG 复用：固定 8a86a552 的 `js/lamp/s06_key.js:178,211,215,236` 仍有逐时灯焰闪动、灰尘及时间 uniform，`js/lamp/shaders.js:513–514` 胶片颗粒也逐时改变。保留原效果，192 帧逐帧实际渲染。
