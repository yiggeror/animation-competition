# S24 bite-fix independent review

结论：固定组合“1e64ae9356d6335430d4783cf4976e1569ed1923 的 S24 入口 + 93705f2f4d910a3b4805c602e8cc2c5bc2adda16 的共享 S23 + 本次新 MP4”通过本轮帧级独审。未发现新的阻断项。旧版嘴喙分离已消除。整合不可只运行云分支旧共享 S23。

## 实际画面

- 从固定 Git 对象取出新 S24 MP4，以本机 ffmpeg 独立解码全部 60 帧；1920×1080、24/1 fps、2.5s，1 条视频流、无音轨。未启动浏览器/监听服务/项目渲染，也未重新编码视频。
- 实看全 60 帧嘴喙局部、九曝光及末帧全景、000/024/040/059 的 2 倍嘴喙/杆/层次局部；龟嘴持续夹在鹤喙末端，F000 至 F059 不再出现先前约 155px 的空隙。接点在完整 S24 画面的左下区域，约 (548, 984)，不会因人物换图重新松开。
- 幕上龟、鹤保持静止，人物既有转头、微抬颏和落定保留。人物在前、幕上皮影在后，鹤颈被人物头发/肩遮挡的边界稳定，未见皮影突然盖到脸、衣服前面或新增层次翻转。
- 在可见画幅内，杆线保持连续；S23 末的龟头签及壳签仍随本体，S24 不出现离开所属关节的漂浮签或穿到人物前面的新杆。S24 下端在画外的部分不作额外视觉保证。源码同时确认 turtleRods(tr) 使用修后根点。
- 跨镜小片单独解码 8 帧：S23 F118/F119 → S24 F000–F005。每帧时间戳相隔 1/24s，未多出停顿帧。逐帧与对应两个源 MP4 独立解码比对，RGB MSE 0.9598–2.0379（切换片二次压缩差异）。幕正面切到背面后左右反转与机位相符，两边均保持嘴喙接触，没有回拨到甩头中段。
- 本次实看方式是独立解码的逐帧/联系表检查，没有声称完成显示器原速播放或整片终审。

## 不变范围和原行

1. s24_drawn.js 与 155d25986b9d6bb38acc8f09043ca74922e4dd16 直接 git diff 只有第80行：sheet23(3.4+0.1*u,env) → sheet23(5,env)。第11–13行相机/曝光/雾/注册、第15–25行九图曝光、第75–85行人物 cards 路径均未改。
2. 对九张原生人物 PNG 逐张读取实际 Git 字节重新 SHA256；旧/新 Git blob 9/9 一致，SHA256 9/9 命中入口常量。F032 = cd01c1cc946011cc5d050498a16c83a84d197ca25221792e779bdd5d9d4e3e43；F040 = 724d5c1c2516e4720bd1905e14b1bfd104f142fe41bc399877963886b69816b8。完整表见 independent_native9_hashes.json。
3. 曝光仍为 000×6、006×3、009×3、012×3、015×4、019×5、024×8、032×8、040×20。对新 MP4 全60帧人物区域做高通归一化模板分类，60/60 与此曝光表一致，最低相关系数0.99743。此数值是附加核验，实看结果不依赖该分类。
4. 运行清单中的23项共享输入，以 Git blob 对比155与937，唯 js/lamp/shots/s23.js 发生变化；crane、turtle、choreo、puppet、渲染/灯光/场景等共享输入未变。
5. 修后 S23 源码与包内 provenance/s23_93705f2_source.js.txt 字节完全一致，SHA256 6d09ecaae7e518557ef961af858a301adeda8e74300c753b58605ea6b201632e。第10行嘴点[57*1.3,-4*1.3]、喙点[126*1.35,1*1.35]；第14行1.2–1.6 ease；第24–25行根据两个接点修龟根点；第27行使用 turtleRods(tr)，数组返回次序仍是龟、鹤。原有 shake/角度计算未改。

## 整合注意

云分支1e64ae9里的 js/lamp/shots/s23.js 仍为旧 Git blob 88a9a54464980ca572b9747b9813a9f83b81a03b；本片正确依赖93705f2的7bf079d18839964271c3e743247509ed3840326d。必须配套新 S23。入口第10–12行旧 SOURCE_SCENE_COMMIT 与 sheetTimeOffset/Scale 是保留元数据，不能据此还原本次渲染；实际调用以第80行和已核运行清单为准。该分支不等于自包含运行快照。

## 本地证据

- decoded/F000.png … F059.png：新整镜全部独立解码原尺寸帧
- 01_all9_and_last_independent.jpg：九态及末059全景
- 02_all60_bite_closeups_independent.jpg：全60帧嘴喙局部
- contact_rods_F000_2x.png、contact_rods_F024_2x.png、contact_rods_F040_2x.png、contact_rods_F059_2x.png
- 03_cut8_independent.jpg：跨镜8帧全景
- 04_cut_contact_independent.png：S23末→S24首嘴喙局部
- independent_pixel_checks.json、independent_exposure_classification.json、independent_native9_hashes.json、independent_runtime_blob_diffs.json

MP4 SHA256：
- S24_scene60_bite_fixed_1920x1080_24fps.mp4: 4c11a2c16fcf25e4b49fa69a5f078c2a75c22c65dff6b8a8767a4545c70ca55c
- S23_to_S24_actual8_1920x1080_24fps.mp4: f488e86ed86e9a5e543317a282bcbf99846abc3b4ba1c18949405637840ac89e
- S23_fixed_tail118_119_1920x1080_24fps.mp4: 39e6587ecc07c52290ce8ca4d773c566f1611d4ebb6ee72be9bc208360f33637

Git来源： https://github.com/yiggeror/animation-competition/tree/1e64ae9356d6335430d4783cf4976e1569ed1923/collab/reviews/cloud_s24_20261018/scene_candidate/bite_fix_93705f2
