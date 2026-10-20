S12正式接景，当前真实前半000–105已完成；完整8秒待后半采用包，不用末张补缺。

- [真实前半MP4，106f/1080p/24fps](front_actual/S12_000_105_actual.mp4)
- [实际关键帧接触表](front_actual/contact_front_000_105.jpg)
- [运行记录](front_actual/runtime.json)、[前半读回](front_actual/front_readback.json)

生产入口 `js/anim/s12_drawn.js`，资源及完整192帧接口在 `assets/chars/g12/sequence.json`。当前仅公开000–105有采用行，106以后会明确报缺，未采用106参考或假设不存在的后半原画。

实际Chromium画布逐帧进入ffmpeg图片管道；只保留8张关键图，未落整套全分辨率序列。人物与双杆随同一曝光保持；真实 `makeCrane/solve/pointOn` 画纸偶与两根有限杆，原有马灯光、背景与镜头继续实际运行；无旧G/groupM/squash或代码人物动作。前半22曝光行含064复用060，不将106曝光帧计作新原画。

全部生产素材已复制到正式资源路径，运行不引用reviews模块/图片。当前采用表来自本分支公开锁稿，后半包到齐后按主协调正式采用manifest绑定；若前半来源一致，将只渲后半并无损拼接8秒。当前MP4为无声画面验收片，未改EDL或音轨。

最短运行：`node tools/js/render_s12_stream.cjs collab/reviews/cloud_s12_20261018/formal_scene_20261020/front_actual --first 0 --last 105`。仅在确需重渲时执行；已有真实结果保留。
