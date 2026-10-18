# S08首33帧 · 实际增渲030–032并复用已核30帧

固定源76ff15e0800e51504bcfe10fec6739556057ea07，入口`collab/reviews/20261018_2003_s08_first33_scene/s08_first33_scene.js`，入口SHA067903e959df59eb44e008932bc0254e4ce24bea8dc3cd39e4544c213633dfc8。没有修改源模块、drawn、背景/灯或绘图资产。

[33帧实际场景MP4](S08_first33_1920x1080_24fps.mp4)：1920×1080、24fps、1.375秒、无音频，SHA13b41cc3b2f3170510d1b7f0b35cde36fcbe86b98214b2717cd55a9f7074938f。仅一次实际Canvas增渲030–032；000–029逐张SHA核对后复用54ae43dd3e5f7d869bc0b3000585bfbaf7638713的已审实际缓存，详见[旧30帧账本](old30_saved_PNG_baseline.json)。只做33帧组装编码，未全33帧重渲，未制作033或以后。

已实看[029–032完整解码](00_requested_actual_decodes.jpg)、[整臂/桌前景](01_whole_arms_table_front_actual.jpg)、[低杆/升罩](02_real_low_grip_rod_globe_actual2x.jpg)、[新柴头火根](03_match_head_actual3x.jpg)、[唯一盒和原影](04_single_box_original_contact_actual3x.jpg)及[近腕衣缝/前后遮挡](05_near_wrist_seam_foreground_actual2x.jpg)。029→030头颈胸领和双臂共同前转；近腕衣缝连续，近手位于远前臂前；远手留低杆、罩留高、灯芯未点燃。火焰根落实际柴头(1148,717)，没有留旧头位置；桌上单盒保原接触影，桌前沿遮挡正常。030–032是3帧曝光，非动作插值。作者逐项实看过，原速节奏/自然度仍交Astra终审，不登记整镜ready。

[33帧验证](actual33_validation.json)逐帧核源/编码顺序，最大MSE9.45593；[ffprobe](ffprobe.json)、[静态回归](static_regression_run.json)、[实际作者记录](AUTHOR_REVIEW.json)分开保留。静态120子帧旧合同一致不冒称实际图像证明。source box1665有效像素及RGBA保持027，body/arms无重复盒；机械角/升罩值是源合同，不冒称图像量测。

[执行来源](render_provenance.json)与[核验工具](tools/check_actual.py)齐全。复核需固定上述源提交，保留`build/S08_first30`30张缓存及`build/S08_first33_increment`3张，使用仓库`tools/js/frames.cjs`；系统Chromium覆盖shim随包。执行中一个HTTP404未报告URL，未推断成favicon；未观察到pageerror。
