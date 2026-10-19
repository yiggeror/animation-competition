# S29 048–071：060完整衣域零调用修复及原场景24帧

本次只修复060前襟—侧衣—下摆与远袖窿衣料接合。新增生图0；048、054、066原RGBA字节不变。原场景曝光为048×6、054×6、060×6、066×6，共24帧，1920×1080、24fps、1秒、无音轨。不代表S29全288帧通过，不登记ready。

## 实际交付与查看

- `S29_F048_F071_ACTUAL_SCENE_1080p24.mp4`：浏览器按原机位/灯光/时长实际绘制，ffmpeg编码。SHA256 `5c8ed0c46726c8b210341b5bee74813996c2dde9a1b31800829a0ef2d69e9691`。
- `ALL24_ACTUAL_DECODED_CONTACT.png`：编码视频全部24帧回解的顺序联系表。
- `THREE_SWITCHES_ACTUAL_CLOTH_1TO1.png`：053→054、059→060、065→066实际回解原输出尺度。
- `decoded_keys/`：8张实际回解关键PNG；`keys/`为对应原Canvas输出。
- `F060_FULL_ON_GRAY.png`、`F060_COMPLETE_ARMS_AND_BLOUSE_1TO1.png`、`F060_FULL_SEMANTIC_BEFORE_AFTER_1TO1.png`：真实修复图及前后对照，非只检查文件存在。
- `ACTUAL_BROWSER_RUN.json`、`FFPROBE.json`、`DECODE_CHECK.json`及`ACTUAL_DECODED_VISUAL_REVIEW.json`：原资源响应、源码锁、帧状态、视频实测与有限视觉结论。

主审与现有只读云复审均实际打开全部24帧联系表、三个换态1:1、048/054/060/066完整回解帧。054近掌离开原neck3夹点并悬空，060完整近前臂/掌落在布面、位于鹤颈前，066近掌保持压布、远手随同源布夹点向内收。原鹤龟及四根杆未重画，杆线方向稳定；未出现旧衣摆灰白弯带或旧远根蓝三角的大断口。

有限待核：060右领肩有细的接线（母画约x488–519/y380–412；实景约x767–798/y375–407），远袖内缘仍有很小的不规则描边。此小段没有因此新增全臂断接，但不宣称所有接缝为零、完整包裹动作已结束或整镜ready。060前襟与衣花相对054/066仍有原生绘张差异，不称像素连续。最终取舍由Astra实际看片。

## 同源修复及锁定

输入来自已归档的 `15061c1cee0b779abca0ae39ae137a3595cf8684` 三张原件及其完整人物层。本次060唯一原件SHA256 `3fc6425ff459cc279c19adbd309669ec591be06387e4f964afd0cece7a251c1e`。逐字提示词、实际请求/三输入、原始工具返回与未改原件仍在相邻 `F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F060/`，未重新调用或替换原件。

`repair_full_semantic_domain.py`从同060原件提取连续花蓝衣面，统一接回前襟、侧衣、下摆并延伸到固定棉布后方；避免追逐旧窄衣摆负形。完整远臂注册矩阵不变，只从有效远袖遮罩剔除误包含的旧侧衣三角及描边1063像素。对原注册层独立核验：删皮肤0、删玉镯0，域外远臂RGBA差0。头颈可见RGBA差0，近臂和有效远臂不透明前景差0；两手及夹点没有新变换。

同源棉布、完整母片、真偶四杆的SHA见 `SEMANTIC_SOURCE_AND_LOCK_CHECK.json` 与 `SOURCES_EXPOSURE_AND_T_LAYER.json`。新060整图SHA256 `b2ac15d0a65f96dab725a6dff9ddb796bc1f6b980b50055f834b0131e69cfae3`。

## 渲染范围

`scene.js`仅在本独占review目录使用原`js/paint/shots/s29.js`的相机/灯光/背景。浏览器路由只读附加export以访问shot；磁盘生产模块不改。旧奶奶代码扭曲图由四张完整画稿替换，保留已批准整人下移30输出像素，排除旧小满接龟层。没有沿用代码人物动作，没有触碰共享文档、EDL或声音。

在仓库根可用`NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node <本目录>/render_short.cjs`重放，`python <本目录>/decode_review.py`仅回解已有片。此次已实际执行一次24帧实渲，原四项受保护场景资源渲染前后SHA相同。重新运行修复脚本会重建静态层及待审JSON，不能据此取代实际视觉记录。
