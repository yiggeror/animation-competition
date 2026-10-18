# S04 新接地影＋034最小修色，待真实72f

入口 js/anim/s04_drawn.js，SHA256 07266e038367d1e2a0887ea9443665b9497b30ccc0b9b11e1190bf5c11ce26b9。timeline fee7ece8acb1bc186ca607cdd2c0b941b98d0690564e88e8ae3c33073c593f02；034 PNG已是e7ea1815ad25075ca3c7ce45a9d3ffd5befc49214620208b94c929162aa4be5b。五张图均assets/chars/s04/，原路径齐，不依赖reviews。

本轮只增Opus a8a0f061原helper支持的三层contact：X a=.4 blur=3 sy=1 dx=-2 dy=3；G a=.45 blur=4 sy=-.07 skew=.5；凳 a=.45 blur=3 sy=-.1 skew=.5。值与同场景S01一致。剥除三字段则与原S04代码逐字节同；机位、F7唯一灭灯、手机遮挡光晕、时表均未改变。034修色证据另见20261018_1650_s04_color_minimal。共享helper不由本轮改。

命令：
node --require <existing Chromium shim> tools/js/frames.cjs /js/anim/s04_drawn.js build/s04_contact72 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 3 --mp4 build/S04_contact_color_final72.mp4

核真实0–71共72帧，解码000/006/007/008/021/022/027/028/033/034/071；看G鞋/凳腿影接地、X身肘贴席无假双身、灭灯前后影子不浮。CONTACT_AND_COLOR_DELTA.json、TEST_RESULT.json是代码/原像素检查，不能替代真实Canvas。旧d55872f不含最终034/新contact，不能借为本版视觉通过。
