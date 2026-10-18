# S08 首14帧合成候选（非整镜ready）

入口：`s08_first14_scene.js`。24fps，000–013，共14帧；014起抛错。

冻结来源：87d420ed171eb611dc8f14dacd586de20fd5790a 的 `collab/reviews/20261018_1654_s08_first6/` 五原图，不重复上传。曝光000×3/003×2/005×1/006×3/009×3/012复005×2。

10个原RGBA互斥层，重建逐RGBA精确等于冻结源；000沿23ced013已审层，003/005按实际新手臂重拆，006/009臂像素验证同005。人物x0/y0/sc1，原背景/桌/凳/灯函数字节不变，桌前沿981、灯底(1415,965.6)、机位(960,540,fit1)。003柴头实际接触擦面；005离盒后火和暖光从真实柴头(1074,782)起。006眯眼、009回开、012正常。无芯火/罩动作。原灯脚影保留，新增桌肘接触影仍待单独诊断。

结构、模块接线、层SHA、原场景函数和RGBA完整性测试通过，详见INTEGRITY.json；接触图是原图坐标核，非Canvas成片。本机Chromium在启动socket被拒，正式提权重试同样失败，真实Canvas仍0帧。须在现有云渲环境实际核000/003/005/006/009/012及14f原速片后再验收。

```sh
node tools/js/frames.cjs collab/reviews/20261018_1721_s08_first14_scene/s08_first14_scene.js build/S08_first14 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first14_1920x1080_24fps.mp4
```

依赖原仓库renderPaint/loadImg与lamp/flameShape接口、bg_01_room_wide原背景及既有frames.cjs，不改公共helper、EDL或音频。
