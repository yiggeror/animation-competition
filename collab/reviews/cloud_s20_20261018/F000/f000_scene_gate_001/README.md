# S20 F000：零调用清理与实际CAM20候选

**限定清理完成；接景待Astra裁定，未放后态。** 高鹤签使鹤与马灯重叠、上部出框，两个C偶端在正式主帧不够清楚，不能只凭数学共线签通过。

- 唯一母态：`cleanup/S20_F000_master_clean.png`（1672×941，SHA256 `55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8`）。同423715衍生图仅颈肤295像素减橙偏、亮度最大差0.435/255，恰346个获准框外alpha1点清零；两mask外RGBA零变。mask、颈前后图、重放脚本与数值齐。不复审已过两腕前襟。
- `CAM20_F000.png`是真实完整WebGL2场景通道1920×1080首帧；`CAM20_F000_same_camera_tall_QA.png`为同F000/同机位/同焦长加高视域，供实看脚影和鹤。裁片`qa/feet_contact_crop.png`中四鞋接地影；正式中景本来不含脚。未签整镜。
- 共享源`88262d20d13c1901d41bf265242d93895f046670`逐文件blob/SHA见`source_manifest.json`。相机、exp.26、fog.5、房间、床单、灯、月光原值。人物整对同尺度，无镜像/独立缩放/代码掰动作，孩子与奶奶画稿高度比0.844。首次固定卡片深度使孩子左缘误穿幕，已在独占适配器按实际平面修材质深度；失败场景保留在`qa/rejected_constant_depth/`。共享源码未改。
- 四签实际握轴→原机构part/at固定，G.L=C_B+C_N、G.R=T_H+T_S、孩子0接触。偶面与杆端同仿射，龟偶端可见；鹤偶端受灯/出框影响。候选偶面只重新注册位置/整体朝向：鹤facing=-1/整体角-.4/源F000颈混合.25，龟facing=-1/整体角.3/其余源F000。未弯杆、换身份或改人物握轴。坐标、偶姿态、保守边界与鞋底平面偏差见`*_geometry.json`；此布置待审，不是最终批准。
- `next_handoff_batch_reference.md`已备000–035曝光、完整体量和008→020→032接触合同。先裁定母态接景，再一次核批次参考，段内作者连续生产/自审；这些参考及后态当前均未生成。

本批新模型调用0，累计历史3请求/3原件，提示词/原始请求/模型原件仍在相邻历史目录。两轮场景渲染均为同F000，每轮正式画幅与加高QA各1张，共1动作状态；没有动画序列、Blender、付费服务/API或全片渲染。

最短复现（已有Pillow/numpy/scipy、playwright、`/usr/bin/chromium`）：

```sh
python collab/reviews/cloud_s20_20261018/F000/f000_scene_gate_001/cleanup_master.py
python collab/reviews/cloud_s20_20261018/F000/f000_scene_gate_001/prepare_registration.py
node collab/reviews/cloud_s20_20261018/F000/f000_scene_gate_001/render_f000.cjs
```

适配器对t≠0报错。仅交本独占目录；不改Opus实现、其他镜头或共享文档，由主协调整合。
