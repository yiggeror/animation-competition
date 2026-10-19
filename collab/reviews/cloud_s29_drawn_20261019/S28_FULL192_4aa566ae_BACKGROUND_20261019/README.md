# S28 固定 full192 后台实跑

固定源 `4aa566ae2714513ef54ae30bc403cf50dde5941c`，浮点深度入口 `8a86a552fba1a822aae0f27ca53e2b0defb4e392`。本目录只放启动器和真实状态快照，未修改执行器或生产代码。

后台监督进程64780、渲染64804、HTTP8197进程64802，已实际查活；监督进程PPID=1，已脱离启动工具会话。实际每时间帧渲染，逐张记录SHA并流入ffmpeg，无同姿PNG缓存。只保留11张原PNG。S29绘图与此并行推进，未串行等片完成。

实时文件在 `/tmp/s28-full192/`：`RUN_STATE.json`、`FRAME_SHA256.jsonl`、`RENDER_STDOUT.log`、11关键帧和最终`S28_FULL192_24FPS_8S.mp4`。当前进度见本目录最新快照。完成后应检查`FULL192_CHECK.json`和实际影片；RUNNING不代表192帧或全片门已通过。不要再次启动现有执行器覆盖账本。
