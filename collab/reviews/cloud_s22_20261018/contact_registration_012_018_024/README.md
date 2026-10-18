# S22：012/018/024同raw零调用局部注册对照

三图结构已获Astra双实看通过。本次仅处理其指定的局部注册，原始生成图和提示词仍保存在上一提交 `f10d7e6dc00c4508383df09377144602cba0abc3` 的 `contact_012_018_024/`，字节未改；没有重生成、整图旋转或新增状态。

[F012注册PNG](candidate/F012_registered.png) / [F018注册PNG](candidate/F018_registered.png) / [F024注册PNG](candidate/F024_registered.png)，均1672×941 RGBA。

[原图→注册图实际接触近图](qa/before_after_contact_native.png)、[锁000和三态同原尺寸对比](qa/registered_progression_native.png)、[6/6/12原曝光对照片](S22_registered_contact_compare_6_6_12.mp4)。对照片共24帧/24fps/1秒，对应原012–035，已解码0/6/12/23核图；不是场景渲染。各态2.5×接触图、灰/白/黑底全图、实际解码和成人前景mask叠图均在 [qa/](qa/)。

孩子与单签采用已锁000的真实绘图像素，成人原图留作后层，原成人前景拇指与下缘四指保留在前层。只在原接触边界做软接与小缝连接：018/024约787/1001个需接回像素，颜色来自锁母孩子和原成人的相邻皮肤；接触侧明暗从原图借回，12px范围平滑过渡，不给整手平涂或新画场景光。mask只做实际图像分层，不生成角色轮廓。

**注册证据：** 三图的腕褶、可见掌面、孩子拇指甲、拇食夹点与单签五处检查区，相对锁000的可见像素RGBA最大差均为0；杆轴斜率、截距与角度完全相同。成人前景核心分别10,799/21,981/23,873像素与各自raw RGBA逐点相同。见[锚点复核](provenance/anchor_proof.json)、[像素保留核对](provenance/pixel_invariants.json)和[所有mask](masks/)。

**曝光判断：** 固定孩子与签后，012→018能读为包指；018→024仍以成人掌背抬高和外轮廓变化为主，四末节没有清楚的共同向内收束。暂不将这版标为“轻收落定已过门”或生产ready。成人原末节没有为制造动作而改动；[可见末节投影区域的中心变化](provenance/adult_terminal_observation.json)也记录了这一点，这些中心不是骨节测量。

按Astra要求，附 [最小末节/接触线局修提案](minimal_terminal_patch_proposal.md)，仅建议下一步在024四末节接触侧约2–4px局部调整，当前未执行。孩子、签、成人拇指和掌腕仍应冻结，不整手重抽、不增030、不开036。接回后少量内侧双轮廓也列入同一次接触线复核，不冒称已锁生产。

[完整反馈和输入SHA](provenance/input_authorization.json)、[重放脚本](register_same_raw.py)、[核查与曝光对照脚本](build_review.py)。重放：`python collab/reviews/cloud_s22_20261018/contact_registration_012_018_024/build_review.py`（Pillow/NumPy/SciPy/ffmpeg）；保留全部输入、输出、mask、命令和SHA。

本次图像调用0次，S22累计仍5次尝试/4张成功原图/1次失败。曝光CSV、计划JSON、锁母和三张raw均未改；未碰生产模块、共享文档、机位、音频或ready。交原独立分支，待Astra审查注册和末节局修方向。
