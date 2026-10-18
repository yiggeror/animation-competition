# S22完整120帧实景候选：背景四推已延后0.1秒，待整镜双审

最新Astra实审要求背景四推延后0.1秒，已按唯一曲线修正重渲本镜120帧。[指定四组三帧实际解码、旧新局部和时间对照](turtle_timing_fix_20261018/README.md)；12人物图与曝光/材色不变，四个窗口外80张原帧逐字节一致。以下当前视频及SHA均已换为本次新片，仍待整镜双审。

[实际实景MP4](scene120/S22_actual_scene120.mp4)：**1920×1080、24fps、120帧、5秒，无音轨**。从共用`dev/view.html`正式Canvas入口逐帧捕获，包含已批准布景、真实乌龟、场景光、慢推、暗角和颗粒。视频完整SHA256：`2370ae5b951a98e22ab1ece6ab082f4c0489850e0f614a43a59728f2b01378d2`。

Astra最新实审已通过114，并明确要求108指定外缘同raw清理后直接接景。[零生成小修](../F108_edge_cleanup_20261018/README.md)先交提交`2d99e52aabf7abed5ccc3b116f06f3d646e3bf85`。本镜仅绑定最终108 `e0d31242883ad1dca5e5ce1c838257228e5d980ace1605ea93e2a31349f5a704`；114保持`74b692c116bf4d72e7d0fb684910b852e4c91ed32cfbe84d704e22a44f217112`。[尾态授权记录](tail_lock.json)、[最终绑定核对](provenance/final_binding_checks.json)与[资源映射](resource_map.json)一致，实际浏览器请求的新108返回200并通过字节SHA验证。旧人物层包`df9f16b`保持原字节，旧108不参与本次实景。

[12态实际解码总览](qa/actual_12_states.jpg)、[末态底边实际MP4放大](qa/actual_tail_lower_edge_6x.png)、[108实际全帧](scene120/decoded_actual/F108.png)、[114实际全帧](scene120/decoded_actual/F114.png)。全部120帧已从本MP4回解并逐页实看：[0–23](qa/actual_decoded_second_0.jpg)、[24–47](qa/actual_decoded_second_1.jpg)、[48–71](qa/actual_decoded_second_2.jpg)、[72–95](qa/actual_decoded_second_3.jpg)、[96–119](qa/actual_decoded_second_4.jpg)。108底部没有竖尖或下拖边；107→108、113→114及119已放大检查，真实斜黑轮廓与接触群保留。[作者实际看图记录](provenance/author_visual_review.json)。

保留12原态及原持帧：000–011、012–017、018–023、024–035、036–041、042–059、060–065、066–083、084–089、090–107、108–113、114–119。[逐帧120行最终源图/SHA映射](S22_final_frame_bindings_120.csv)。其他11态RGBA和所有曝光区间/持帧与`b459d126`逐项一致；人物原图左上对齐按1920/1672等比入画，无额外旧人物抖动或动作代码，不程序接第二签。

[S22_drawn.js](S22_drawn.js)导出`DURATION=5`、`FPS=24`、`TOTAL_FRAMES=120`、`renderFrame(ctx,t,W,H)`和`render`。实际模块SHA `a5d4596d86e9e8a485b70ad3f567716ee6878637f96236b4003a59c42d659d1f`；相对已备入口仅`turtleStep`一行区间改为1.5+k～1.82+k。正式路由：

```text
/dev/view.html?mod=collab/reviews/cloud_s22_20261018/scene_integration_120/S22_drawn.js&w=1920&h=1080
```

场景参照协调分支`c920857531ac60a63d1b09a848698854856ab657`，S22场景代码SHA `c458f6c27161869ec5761bdc2c02fff4f7da17134da1c6500d145dc31cf86c3c`；保留床单径向暖光/褶子、实际乌龟素材及背景运动、一次场景乘光、5%慢推、暗角和颗粒。[依赖SHA核对](provenance/scene_reference.json)。

已实际执行预检、整镜捕获和独立回解检查，资源失败0、旧h22贴图请求0。120张原Canvas PNG保存在[frames/](scene120/frames/)，24张状态首尾实际解码图保存在[decoded_actual/](scene120/decoded_actual/)。[完整捕获清单](provenance/actual_scene120_manifest.json)含120原帧SHA、实际HTTP与ffprobe结果；[独立检查](provenance/actual_scene120_checks.json)含120解码帧SHA。复现命令：

```bash
node collab/reviews/cloud_s22_20261018/scene_integration_120/preflight.cjs
node collab/reviews/cloud_s22_20261018/scene_integration_120/render_scene120.cjs
python collab/reviews/cloud_s22_20261018/scene_integration_120/verify_actual_scene.py
```

全部改动仅在本镜独占审查目录，未动共享EDL、音轨、ready、生产模块或主分支。[范围检查](provenance/production_scope_check.json)。本轮新图像调用0；原始生成输出和完整提示词仍保留于各原包。当前为**实际场景无声审看片，待Astra整镜双审**，未登记生产ready。旧`capture_guard.json`及布景独图属于接景前门禁验证历史。
