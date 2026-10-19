# S15 已过实际192f的生产路径迁移

唯一入口 `js/anim/s15_drawn.js`，八张真实原画原blob迁至 `assets/chars/x15/`。仅改一个资产URL前缀；注册、F144整层0.94、原相机/幕/灯、8态192f曝光不变。EDL/音频/共享helper/ready均未改。

已实际主审基线：云提交 `6abc6cdadc7aeaad2893f0ef87c680a2000b3208` 的 `collab/reviews/cloud_s13_20261018/render_assist/s15_scene192/S15_scene192_1920x1080_24fps.mp4`，SHA256 `c0e2a0cd0ba9ebd6ed1f6829df558f4e452e680a33007126f9c57e492e76ffac`。192帧/24fps/8秒1080p无声。原亮度实际画面中解臂、手落膝、整身前倾可读；前景暗/鞋凳下缘裁切保原镜头表达，不重画。见 ACTUAL_REVIEW.json。

待现有云仅新渲生产入口一次，对基线全部192源Canvas PNG逐字节比较；八资产核blob/SHA，资源不可再请求reviews路径。实际片一致后才ready。

```sh
node tools/js/frames.cjs js/anim/s15_drawn.js build/S15_production192 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S15_production192.mp4
```

旧实际192无需重渲。新生产资源日志、192个原Canvas SHA与对照摘要即可，避免重复工程上传。
