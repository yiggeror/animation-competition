# S12 F012 · 仅门襟下尖同raw明度收尾，附同时间真实单帧

沿已审 `1c9199121eea99f2434cc39c864eb96c1aba1819` 的F012，按 [Astra本轮完整授权](provenance/astra_tip_authorization.md) 只修静态门襟下尖的明面/背光面。**0生图、0新姿态、018未开放。** 上一版103ed4f原生、原始52c6faf绘图、完整三输入与c6477cb修订prompt都保留在父包/原修正包，没有覆盖。

- [唯一修后F012](candidate/F012.png)，1024×1536 RGBA，SHA256 **`063bc020f65f3e9485a57984f20703f0fbc96667a2f5a046ad713ee51d1beb88`**。
- [母态/修前/修后完整布尖6倍](qa/02_native_complete_tip_context6x.jpg)、[全身同尺三图灰深底](qa/01_native_whole_three_same_scale_gray_dark.jpg)、[完整语义范围/分面/实际改色mask](qa/03_semantic_faces_and_actual_change_masks.jpg)，已实际打开复核。
- [最终真实F012 Canvas](actual_scene/F012_Canvas.png)，1920×1080/绝对t=0.5，SHA256 `6ba342698cb32c6488118ebad9281ca3f013676b83a7b9956c83a11a1a924f94`；[同时间实际布尖前后8倍](actual_scene/00_same_time_actual_F012_tip_before_after8x.jpg)、[实际身体局部上下文](actual_scene/01_same_time_actual_F012_body_context3x.jpg)。
- [单帧静音实际片](actual_scene/S12_F012_placket_tip_1920x1080_24fps_1frame.mp4)，1920×1080、24fps、仅1帧，SHA256 `f01a9dc919242a9d604cf10a24470489e3e84812c5980eef49510330b1f2344a`；[完整解码](actual_scene/F012_MP4_decoded.png)。

## 这次只改哪里

完整布尖按实际折片轮廓分明面/背光面；只改 **2,717个RGB像素**，实际bbox `[464,940,529,1047)`。整张alpha逐像素不变；布尖外RGB、上领/中门襟y<940、皮肤/头发/裤子、两手及其他已过衣面逐像素等于上一版103ed4f。折线墨迹保留，无位置变换、缩放、拼贴或重画。左邻片610px保护域复核为原字节，没有把相邻衣片带进最终改色。

明面做小幅同面RGB平移；背光面按母态同位置的蓝底和受影花瓣对应内核校准正斜率RGB映射，让两种材料一起回到受影明度。只在颜色上逐像素映射，保留原有花瓣边界位置、折向及纹理明暗顺序；不抹图、不模糊纹理或复制母态花纹。2px编辑边界羽化，2px分面过渡；所有mask、校准坐标与完整统计见 [原生验证](qa/native_tip_verification.json) 和 `masks/`。

| 布尖材质/面 | 修前相对母态ΔRGB | 修后ΔRGB |
|---|---|---|
| 明面完整蓝料区 | (+9.95,+7.72,+6.84) | **(+2.84,+2.00,+1.02)** |
| 背光面完整蓝料区 | 约(+11.56,+10.49,+10.68) | **(−0.08,+0.20,+0.46)** |
| 背光花瓣184个固定对应内核 | (+35.35,+32.09,+25.51) | **(+0.15,+0.15,+0.01)** |

不是再次整领减R或整衫调色。花瓣边缘像素没有搬移或替换；花瓣填色和边缘的RGB随所属面恢复受影。JSON也保留独立阈值样本的全部统计与样本数；明面花瓣母态独立亮色样本仅8px，不能将这组小样本均值当整花纹颜色门。主判断由同尺完整布尖、完整蓝料和固定对应花瓣内核共同支持，不称全部原生像素逐点等于母画。

## 同一真实F012时刻，场景只变布尖

最终场景入口与已通过的上一版F012入口 **源码整文件字节相同**，保持 `.70+(275,112)`、t=0.5、原灯光/相机/鹤/双杆/箱布和接地；alpha全等，所以原六接地mask直接逐字节复用。实际浏览器读回的代码道具层和接地影层PNG也与上一版 **逐字节相同**，人物层alpha全等。

真实Canvas前后只有 **1,426个像素** 变化，bbox `[599,770,645,845)`；注册后布尖以外变化为 **0**，见 [实际变化mask](masks/actual_Canvas_RGB_changed.png) / [完整验证](qa/actual_delivery_verification.json)。双手距实际道具层最近约32.02/44.72场景px、人物道具alpha重叠0，与已过接景一致；未碰手、杆、鞋或接地。

本轮有2次同F012实际渲染：首轮检查时发现初稿语义mask稍带左邻片，已把该邻片恢复原字节、收紧到布尖轮廓后仅补渲最终同帧。首轮候选/工具/实际Canvas/MP4/日志完整存于 `qa/iteration01_scope_refinement/`，不混为最终候选。没有重复渲S08或任何其他帧，最终只交当前candidate。

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s12_20261018/d02_F012_20261019/placket_tip_fix_20261019/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/cloud_s12_20261018/d02_F012_20261019/placket_tip_fix_20261019/scene/s12_F012_scene.js build/S12_F012_placket_tip_scene1_final --fps 24 --w 1920 --h 1080 --workers 1 --from 0.5 --to 0.5416666666666666 --mp4 collab/reviews/cloud_s12_20261018/d02_F012_20261019/placket_tip_fix_20261019/actual_scene/S12_F012_placket_tip_1920x1080_24fps_1frame.mp4
```

[实际网络](qa/actual_canvas_network_events.jsonl)、[摘要及真实console URL](qa/actual_network_summary.json)、[17个实际输入SHA](qa/actual_runtime_inputs.json)、[ffprobe](qa/actual_ffprobe.json)齐。最终1次实际输出/1次编码，视频解码MSE=8.374245。0pageerror/0requestfailed；favicon404的实际console位置保留，不称全请求200。图层读回不再次调用renderFrame。

[本轮台账](provenance/repair_ledger.json)、[总SHA](SHA256SUMS.txt)。全程累计S12原生调用仍为4；原件/完整提示不变。只新增本独占子目录，不改共享实现/留言、ready、EDL、音轨或主分支，不用Blender/付费API。交Astra审最终布尖及同实际单帧；018仍关闭。
