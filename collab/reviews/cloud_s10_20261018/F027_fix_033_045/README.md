# S10：027仅修眼，030→033→045，交Astra实审

本批按最新授权完成三张候选，原027与全部旧原件均保留。033从独立认可的030续画，045再沿本批033缓和；没有从027修稿派生后段。全部人物来自真实图像工具输出，代码仅做均匀注册、低透明度杂点清理和明确掩膜采纳。新候选尚待Astra锁定，不签全镜。

## 先看这些

- [027眼部修稿](candidate/F027_fixed.png)：视线改向画左，眼裂介于024和030之间。仅采纳两眼虹膜及必要眼睑所在的镜片内区域；颅、耳、镜架、鼻、颈、衣身在掩膜外逐像素不变。原027在 [inputs/F027_reviewed_source.png](inputs/F027_reviewed_source.png)，不是锁定态。
- [033峰态](candidate/F033.png)：沿合格030进一步整头连颈转向，远耳隐入轮廓，两眼收至闭合。
- [045缓和](candidate/F045.png)：由033小幅回转，两眼仅开细缝，嘴仍轻抿。角度数字只是构造目标，不冒充实际图像测量。
- [六态头颈对照](qa/head_sequence_contact.jpg)，含027失败源与修后并排；单态原尺寸头颈与黑白灰底检查在 `qa/`。
- [实际72帧实景MP4](exposure/S10_first72_scene.mp4)、[实际解码接触表](exposure/actual_scene_contact.jpg)、[逐帧PNG](exposure/decoded/)、[视频核验](exposure/actual_video_manifest.json)。

## 实际曝光范围

| 图 | 实际帧 | 张数/曝光 |
|---|---|---|
| 锁定000 | 000–023 | 1张×24帧 |
| 原024 | 024–026 | 1张×3帧 |
| 本批027修稿 | 027–029 | 1张×3帧 |
| 独立认可030 | 030–032 | 1张×3帧 |
| 本批033 | 033–044 | 1张×12帧 |
| 本批045 | 045–071 | 1张×27帧 |

实际浏览器渲染72帧，1280×720、24fps、3秒无声。MP4经ffprobe计帧，并解码实看000/021/022/023/024/026/027/029/030/032/033/044/045/056/071。未生成072、096，未渲染072–119，无缺态占位。人物基础色无手电斑；来光及045后略退光均在独立场景灯光中，灯光仍交主协调/Opus整合。

## 保护范围与实看结果

027只采纳真实生成的局部眼像素，掩膜外RGBA一致。033、045采用真实返回的完整头颈，按固定胸前花纹均匀注册，无脸部非刚性扭曲；两张的y948–1079固定衣带均与锁定000逐像素一致。清理只处理低透明度外部杂点：033最高被清理alpha15，045为21，源RGB及alpha>24均未改；灰黑发丝与左红珠保护保留。过程、掩膜和重放脚本完整存放在此目录。

实看027已恢复左视，024→027→030→033持续收眼，045只略开。033/045整头、耳、镜架、颈部一起变化，肩胸固定。左侧后领口仍有细小接合毛边，继承030接口，未宣称成片通过；Astra宜复审其实际曝光是否需要局部收边。整体灯光、节奏与最后两态仍未签全镜。渲染日志保留一条未标URL的404，未出现模块或绘图载入失败；不将此记为零浏览器告警。

## 调用与来源

本批实际图像调用3次、返回3张、工具失败0次，形成3张候选；S10累计9次（000及衣带2次，上一批4次，本批3次）。旧027首版及第二版的视线问题原件未覆盖；第二版只作为本次局部修眼来源。

[调用及输入SHA清单](provenance/call_manifest.json)、`provenance/*_prompt.txt`、`*_request.json`、`*_tool_metadata.json`保留完整提示、实际参数及工具来源；`originals/`保留未改原始输出。注册/清理/采纳详情在 `*_preparation.json`；像素与来源复核见 [qa/file_and_pixel_checks.json](qa/file_and_pixel_checks.json)。

实际渲染复现命令（仓库根目录）：

```sh
node --require ./collab/reviews/cloud_s10_20261018/render_assist/use_system_chromium.cjs tools/js/frames.cjs collab/reviews/cloud_s10_20261018/F027_fix_033_045/S10_drawn_prefix_candidate.js build/cloud_s10_first72 --fps 24 --w 1280 --h 720 --workers 4 --mp4 collab/reviews/cloud_s10_20261018/F027_fix_033_045/exposure/S10_first72_scene.mp4
python collab/reviews/cloud_s10_20261018/F027_fix_033_045/exposure/decode_actual.py
```

仅本独占目录交付，S07手机及其他镜头未改，共享实现、留言、ready及音频未改。
