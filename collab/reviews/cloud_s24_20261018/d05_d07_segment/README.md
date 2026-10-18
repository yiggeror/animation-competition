# S24阶段保全 · 015/019已完成，024局修图像调用失败

**实际状态：本批未齐。**015和019已原生生成、逐张实看并过区域色门；024第一稿有正确抬颏/提眉闭口笑但泡袖出画，第二稿修了袖缘却退回019式表演，均未采用。第三次袖缘局修真实调用失败，未返回新图。最新实际shell读写和六份PNG核对通过，不能据此宣称图像端恢复；底层异常文本未留存，无法确认是否同一断连原因。[真实调用失败与实机读回记录](provenance/environment_actual_probe_and_blocker.json)及`requests/F024_call_010_response.json`保留已知事实。

| 可审候选 | 曝光 | SHA256 |
|---|---|---|
| [F015_rgba.png](candidates/F015_rgba.png) | 015×4 | `3eaef2e1fa5e99c308dd46de105bb38d8e97e331f3b801763da152e2aa6ca1ce` |
| [F019_rgba.png](candidates/F019_rgba.png) | 019×5 | `d5f04b6b949a6b96a0c39ec8fe8850f7b2b30f00af835bbe38ddf53c66b4c1a3` |

起点为0b7fc147包中Astra双审锁定的012 `dcbe1e52…`，[本批授权与实际转幅更正](provenance/astra_first3_lock_and_next3_gate.md)已保全。015实际审后才派019，019审后才派024。旧浅母和失败009未作输入，区域颜色始终参考新修母0485c6fe…；原生raw/工具默认文件均完整保留。

实际查看[012及015/019整图](qa/00_locked012_and_015_019_partial.jpg)、每态`Fxxx_previous_current_full.jpg`、`Fxxx_previous_current_neck_ears.jpg`及`Fxxx_B_neutral_NOT_SCENE.jpg`。015仅小进到看住画右上奶奶、嘴角刚提，019头先到、胸肩/领口小跟、近侧自由尾向画左滞后，根仍接头。颏颈/耳根连续、闭口清醒、手肘画外。019右泡袖只在源最右列有1个实体像素相切，未见平截段；024首稿则有88个实体边缘像素/连续88行裁切，明确拒收。角度和尾滞后数值为构造意图，未冒称成图精确测量。

B整层`.70+(590,20)`不变，alpha≥248实体发顶余量01576.7、01970.4场景像素；完整呆毛/短尾可见。两态逐区域均值最大通道差0152.96009、0193.8083（冠发R），均在±4内，保留局部色阶。每态`Fxxx_color_config/validation.json`及mask/weight记录同raw局部语义校色；相对raw的alpha、发部深线/高光保护、材质域外变化0，未用代码转头/变形。新生状态不冒称与母稿逐字节相同。

[12帧中性人物层预览](qa/S24_F012_023_neutral12f_24fps_NOT_SCENE.mp4)仅含已锁012×3/015×4/019×5，对应012–023；[逐帧编码核验](qa/neutral12_encoding_validation.json)齐。没有用019长停或失败024补缺；它不是Canvas接景、完整60帧或音轨验收。

`originals/S24_F024_call_008_REJECTED_sleeve_crop_raw.png`保留正确表演但出画的首024，`…call_009_REJECTED_pose_regression_raw.png`保留表演回退稿，不进`candidates/`。恢复后仅继续`F024_call_010_request.json`记录的同一首024袖缘局修，不重生成015/019，不把旧失败009或回退024作合格前态。请求、实际输入SHA、完整提示词、返回元数据及失败记录均在`requests/`；局修010仅用原024作局部目标，颜色仍由锁母后门控制。

本批实际尝试5次：4次原件返回（2候选、2未采用024），1次工具失败；累计S24尝试10次、原件9份。生产分支、公共代码、S08灯具/放盒、留言、EDL、声音、ready均未动。024缺项需图像端恢复后完成；032/040未开。先交此阶段保全，再执行已指定S08首23帧实际渲染。
