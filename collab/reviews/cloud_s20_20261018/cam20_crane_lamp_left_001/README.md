# S20：372d96fe导演范围内，单张正式CAM20候选

先看 `CAM20_F000_crane_lamp_left.png`（1920×1080真实完整WebGL场景，只渲1帧）。鹤完整处于灯左、画内且不覆盖孩子头脸；人物、掌形/玉镯外域、CAM20、灯、房间、曝光/fog及偶面朝向/尺度/关节姿态/body与neck3局部接点保持。只重定位同一鹤装配并把两根硬签绕原掌内夹点转−48.8024°/−53.3631°，指缝小开口与同一根完整场景杆同轴；旧杆短段清理mask保留。全程图像模型调用0，未批处理。

**仍需导演裁定一处：** 两杆投影经过孩子头后，受前景头部遮挡后从额侧边缘显露。见 `CAM20_forehead_edge_review_circle.png`（原实帧圈注副本，不是第二次渲染）。当前不称“杆轴也避开头域”。固定偶姿态和相机的有限网格检查758个画内样本，18个杆轴避头域，未找到同时鹤轮廓也避头域的样本；这不是不可能性证明。请Astra/Opus看该单帧决定能否接受此后方遮挡，未过整景门前不传播杆角到曝光批次。

导演原文 `director_372d96fe_S20_original.txt`；完整原像素/材料mask、两掌夹点及刚性旋转矩阵见 `rod_rotation_provenance.json`，渲染几何及只读共享源SHA见 `verification.json`。核心8个渲染文件已逐字节核对372d96fe，均未变。实际握杆近图 `CAM20_actual_grip_close_6x.png`。

复现：`python .../rotate_visible_crane_rods.py` 后 `node .../check_and_render.cjs --render`。源依赖固定在同独占目录既有 `F000/f000_scene_gate_001/source_snapshot/`；不改生产/共享代码。首次36f曝光另交cd67a138，未混入此未审构图。
