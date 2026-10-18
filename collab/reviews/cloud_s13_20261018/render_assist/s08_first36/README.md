# S08首36帧实际场景 · 复用旧33＋新增033–035

[36帧MP4](S08_first36_1920x1080_24fps.mp4)：**1920×1080、24fps、1.5秒、无音频**，SHA `b16f1488496c0dc6a100060d36e99d19f80eff1f3b8fb2ae5b868b9ccb509f37`。固定源2a8fcb919cc4efe59169be80650d10621427ef25；入口SHA58ab66325e19ff46d0b295ec428bfc7afd5137a02de6c415582f7fd32179f754。仅实渲033–035，旧000–032按c10fa383账本逐张核SHA后复用；未全36重渲，未制作036以后。

已实看[032–035完整解码](00_requested_actual_decodes.jpg)、[整臂和桌前沿](01_whole_arms_table_front_actual.jpg)、[低杆/升罩](02_real_low_grip_rod_globe_actual2x.jpg)、[柴头与灯侧管](03_match_head_actual3x.jpg)、[单盒与原接触影](04_single_box_original_contact_actual3x.jpg)、[近腕与手前盖](05_near_wrist_seam_foreground_actual2x.jpg)。近手在远掌前的遮挡清楚，远手保持低杆座；真火根(1230,707)接木柴，位于侧管画左且有净空；盒与薄影、桌前唇正常，灯芯未亮。作者指定局部实看通过，Astra原速首36门待审；未报整镜ready。

[36帧验证](actual36_validation.json)含33缓存SHA、36源/编码对应、实际3帧浏览器轨迹、固定运行源SHA及低杆148像素盘与030逐RGBA一致；最大编码MSE 9.43940。[ffprobe](ffprobe.json)、[旧33静态回归132子样](static_regression_run.json)与[实看记录](AUTHOR_REVIEW.json)分开。静态素材/机械数值不是图像实测。旧远手复用档的(1127,800)孤点在运行033中alpha0，未复活。

[原33缓存账本](old33_saved_PNG_baseline.json)、[增量命令及计数](render_provenance.json)、[原始浏览器事件](qa/actual_browser_events.jsonl)保留。实际6次033层PNG响应均HTTP200，但审计接口response.body返回空体；空SHA不当原图SHA。随后[单独只读Chromium字节核验](qa/independent_browser_asset_sha_probe.json)确认3张冻结层图的非空字节/SHA完全一致，未重渲；不冒称这是当次渲染响应的内容哈希。0 pageerror/requestfailed/auditerror，控制台保留一条未带URL404。

工具启动2次：首因自有审计qa目录漏建，在0帧阶段失败；补齐后1次成功实渲3帧、组装编码1次。失败原文/根因保留，复核脚本路径和采样修正也有[记录](qa/review_preparation_corrections.json)。固定源模块、人物图、背景/灯、共享renderer均0改动；生图0，未动S24人物、EDL、音轨、生产主分支或ready。

重查脚本`tools/check_actual.py`需固定上述源提交、保留本交付目录、build/S08_first33旧33缓存、build/S08_first36_increment新3帧及build/S08_first36组装PNG/MP4；这些实际缓存未清理。
