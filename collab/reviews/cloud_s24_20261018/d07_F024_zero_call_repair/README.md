# S24 F024 · 零生成衣片接回候选，交Astra审

环境实际可执行；本轮 **0次图像调用**。唯一取图：[F024_original_pixel_sleeve_repair_rgba.png](candidates/F024_original_pixel_sleeve_repair_rgba.png)，SHA256 `8c695f4020cc00e61b19d26a6818e0aa3c22abf752bb897a88cb3b561e69dd62`。先审此原像素结构候选，**未宣称Astra锁定或最终色门通过**，未开032/040，015/019未动。

call008作为完整表演/头颈耳辫/领胸基体；仅从call009取完整泡袖、荷叶口，原枢轴(850,1015)→(866,1019)、顺时针2.5°、预乘RGBA重采样，沿真实袖窿接到肩根。[两份原件、完整prompt/response及固定SHA](provenance/sources_and_method.json)均保留原路径；失败call010未重试。定位包络没有用作矩形mask。

[灰底全图](qa/F024_gray_full.jpg)、[深底全图](qa/F024_dark_full.jpg)、[袖窿/袖口2倍](qa/F024_dark_sleeve_2x.jpg)、[袖口6倍](qa/F024_dark_cuff_6x.jpg)已实际打开检查；最终袖窿无此前透明细缝，泡袖外轮廓完整，最右实体x1019，留4源像素。全图抬颏、提眉、闭口笑仍为首稿，未借回退稿的头颈。袖根、内袖缝与荷叶实际接合仍请Astra独审，不能用像素核代替结构验收。

**单列窄皮肤接缝：**首稿call008上臂原像素，从源下移区域取样填袖下窄带，逆仿射 `[1,-0.25,373,0,1,24]`；y1401–1471支持，末12行归回首稿，y≥1472整臂逐RGBA不动。此为衣片下面的局部仿射转接，不冒称衣片刚性或纯整层平移。可见接缝只在荷叶下窄带，首稿上臂优先。[源层](layers/call008_under_cuff_skin_source_registered_rgba.png)、[独立weight](masks/under_cuff_skin_weight.png)、衣片层、原位/注册mask及清除域齐；没有代码画人物或补画新皮肤线。

[保护域与实际差分](qa/protected_domain_actual_diff.jpg)及[像素核](qa/repair_pixel_validation.json)：变化91304像素、bbox=(745,1017)–(1024,1472)；定义保护域1443191像素，RGBA变化0，域外变化0。[额外核](qa/additional_protected_domains.json)为整头双尾、脸耳颈皮肤、两整领片及线/AA全部0变化。修复域内alpha按衣片接回改变，未宣称整图alpha不变。头顶至y999及下臂y1472以后整行RGBA均同首稿。

[灰底13f曝光](qa/S24_F019_031_gray_13f_24fps_NOT_SCENE.mp4)、[深底13f曝光](qa/S24_F019_031_dark_13f_24fps_NOT_SCENE.mp4)：019×5→024×8，对应场景019–031，B整层`.70+(590,20)`，1920×1080/24fps/13帧/无声；[实际解码接触表](qa/actual_decoded_exposure_contact.jpg)、0/4/5/12跳点与[编码核](qa/exposure_encoding_validation.json)齐。已实看最终袖区，以及此前同头颈/同表演的019→024解码跳点；024微抬颏/提眉而未回退到019。此为中性人物层曝光，不是Canvas接景、完整60帧、音轨或主观原速验收。

**原色门仍未通过。**本轮只做原像素修复，没有偷偷改受保护头脸RGB。沿已用F019语义ROI检测锁母：冠发均值ΔRGB=(9.11049,5.55349,3.89475)，近/远尾最大差6.37110/6.10402，肤色最大差6.89560；裙色在±4内。[原色测量](qa/color_measurement_NO_COLOR_EDIT.json)明确。结构审查后仍需单独的固定锁母局部色门，不能把本候选当已完成校色的最终024；本轮不扩为重生成、不先开032。

复现：在任意工作树运行`python collab/reviews/cloud_s24_20261018/d07_F024_zero_call_repair/tools/rebuild_repair.py`；核验与13f层曝光用同目录`tools/build_qa.py`（Pillow/numpy/scipy/ffmpeg）。所有更改仅在独占S24 reviews目录，不动共享主分支、Opus实现、留言、EDL/audio/ready。
