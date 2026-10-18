# S22独立drawn模块与正式Canvas接景入口：准备完成，尾态待锁

人物层先交提交 `df9f16b54b6873d3fe36e30d27c7082eb7b4a279`。本目录只准备本镜接景，不改生产主分支、共享EDL/音轨或ready。**当前没有120帧实际场景片，不能以人物层灰底片替代整镜ready。**

[S22_drawn.js](S22_drawn.js)导出正式Canvas约定的`DURATION=5`、`renderFrame(ctx,t,W,H)`和`render`；[资源映射](resource_map.json)绑定12张实际RGBA及SHA，120帧完全沿原曝光表。108唯一`d8094899…80b74f0`、114唯一`74b692c1…f217112`仍等待Astra集中尾态双审。没有WIP顶帧，没有旧暖稿或旧h22两组手贴图。

场景参照最新协调分支 `c920857531ac60a63d1b09a848698854856ab657`，S22原场景代码SHA `c458f6c27161869ec5761bdc2c02fff4f7da17134da1c6500d145dc31cf86c3c` 与本地一致。保留后台床单径向暖光/褶子、实际乌龟素材及背景运动、一次场景乘光、5%慢推镜头、暗角及颗粒；人物只按绘图曝光换张，左上对齐按1920/1672等比放置，不叠加旧人物抖动/平移/旋转，也不程序接第二签。[场景与依赖SHA核对](provenance/scene_reference.json)。

入口：[render.html](render.html)；正式共用入口路径为：

```text
/dev/view.html?mod=collab/reviews/cloud_s22_20261018/scene_integration_120/S22_drawn.js&w=1920&h=1080
```

`tail_lock.json`目前为`pending_astra_tail_review`。未获明确尾态锁定时，正式`renderFrame`与场景捕获脚本均报`S22_TAIL_FREEZE_REQUIRED`，不会渲待审人物整镜。准备入口只显示已批准布景，[布景检查图](qa/preflight_environment_only.png)不含人物、不是整镜候选。

已实际运行：

```bash
node collab/reviews/cloud_s22_20261018/scene_integration_120/preflight.cjs
```

12个PNG加载及SHA/尺寸核对通过，全部120帧绑定与曝光表一致；正式Canvas接口兼容，失败资源请求0，未请求旧h22贴图。未锁尾态渲染阻断也已验证，[实际检查记录](provenance/preflight.json)、[捕获门检查](provenance/capture_guard.json)。

收到Astra明确锁定后，先把`tail_lock.json`记为`approved`，填写实际审批提交和两张最终PNG的完整SHA；若终审改了尾态，则先同步资源映射及最终图，不能只改状态。随后本镜原作者可运行：

```bash
node collab/reviews/cloud_s22_20261018/scene_integration_120/render_scene120.cjs
```

该脚本通过共用`dev/view.html`正式Canvas接口逐帧捕获1920×1080、24fps、120帧/5秒，检查实际PNG资源SHA及HTTP错误，并输出`scene120/S22_actual_scene120.mp4`、全部Canvas原帧SHA、实际解码边界图及来源清单。只渲S22，不启动全片，不调用旧Blender。输出为场景无声审看片，仍不修改共享音轨、EDL或ready；实际片完成后须实看并交整镜双审。
