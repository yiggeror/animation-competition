# S14 可采用静音版：完整240帧／10秒

当前唯一整镜候选：[`assembled/S14_FULL240_10S_BACKSTAGE_CANDIDATE.mp4`](assembled/S14_FULL240_10S_BACKSTAGE_CANDIDATE.mp4)。1920×1080、24fps、240帧、10秒、静音；SHA256 `5b2ed3ff18dc785899724d838cb3741253947e29beb9277b23d92071772f33b7`。

**Library已上传成功**，`library_file_id: libfile_9ded824b9b088191adb710bbf1fba641`。准确回执和本地版本xattr在 `LIBRARY_UPLOAD.json`。

新增原画／生图 **0**。000–131复用已交MP4编码流，原三段120格及新018–029均未重渲；只新渲132–239的108格后段后拼接。完整240格逐帧解码与“原132格＋新108格”源序列严格一致。浏览器实际播放到10秒末，240格、0丢帧、0损坏、无media error。见 `assembled/FULL240_ASSEMBLY_AND_DECODE.json`、`ACTUAL_FULL240_MP4_PLAYBACK.json`。

## 本轮真实解决

- 原奶奶下凳后在幕后的完整头／旧举臂可被原床单遮住，原人物y<550保守区域的可见像素为0。露出的原衣摆、裤腿、鞋仍保留，落在原工作凳对应地面570.3，不能把整人直接删掉。整人等比.335，候选变换(466.45,227.26)，没有分肢拉伸、代码人物或新落臂图。
- 仅用原布真实轮廓作不透明材质遮挡；不扩大布，不移动箱／灯。最初背景中心650露指尖，整人左移6背景像素后为644；初测失败、去幕诊断、修后实景和末态均保全。
- 131近景切回132时已见原采用141起步态，避免无切镜到141突然出现小满。现有141／144／147／156四态各6格，162落稳12格；168–239原15态与曝光不动。准确候选表在 `BACKSTAGE_RETURN_132_167_EXPOSURE_PROPOSAL.json`，尚待主审动作取舍。

先看 [`BACKSTAGE_RETURN_REVIEW.md`](BACKSTAGE_RETURN_REVIEW.md)，以及 `assembled/ACTUAL_ENCODED_095_096_131_132_CUTS.jpg` 和 `actual_backstage132_239/ACTUAL_BACKSTAGE_AND_CHILD_SUPPORT_1TO1.png`。切口四图来自最终主片实际解码。原始108格视频、PNG、日志完整保留于 `/tmp/s14_actual_backstage132_239_108frames_20261020`；运行前SHA／mtime及实际采用源码在 `BACKSTAGE_INPUTS_AT_RENDER.json`、后段 `SOURCE_AT_RENDER_*`。

## 三处收尾已完成：可采用现片

本轮按主协调要求只收尾149→150、179→180和239→当前S15首帧。结论：**采用现有240格静音片，必要补画0**，原曝光和MP4字节均保留。前两处有可见有限动画换张，实际原尺未见足以要求新原画的穿模、滑足、头颈断接或全身比例突变；179→180按真实凳脚统一画布，不单独缩头。239与S15首帧复用同一完整抱臂人物＋木凳，视线与右侧暖幕保持延续，景别／前景亮度变化接受。

看 [`final_three_point_review/README.md`](final_three_point_review/README.md) 与实际解码图／24fps小片。当前S15源码、首画原图和实际正式MP4已对最新共享版本核同blob。可见切接审已闭合，不再要求抽象的整套3D世界相等。095→096省略已获主协调允许，131→132真实遮挡保留。声音／EDL／整片ready由主协调整合，本轮未改。

旧231格分段候选、159原图诊断及前批说明均保全，见 `HISTORY_231_CANDIDATE_REVIEW.md`；旧缺132–140的说明已被本轮实际遮挡和切回曝光候选取代，不再据缺编号自动要求新画。全程只改本独占目录，未触碰S29、S31或共享文档，未新启代理。
