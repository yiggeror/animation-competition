# S20 单张正式CAM20：鹤杆继续上抬，零生图

基线已本地解析为完整提交 **445d2921aead0d6cbd20d142d2d341f9564b0e6c**。只新增本独占包，未改原445d包、共享实现或文档。

先看 `CAM20_original_circle_area_before_after_3x.png`（原圈同一坐标区域，前后均取正式实帧，无重绘）及 `CAM20_F000_crane_lamp_left.png`（本轮唯一正式1920×1080实帧）。下方C_B绕原高镯掌夹点向画面左上抬 **3.938481°**，C_N抬 **4.381702°**；同一鹤装配根位置从[1.8,1.14]到[1.8,1.21]，原完整偶姿、尺度、body[-75,6]与neck3[10,0]接点保持。杆不折，指间短段已用显式小mask同轴接顺。

实际结果：原圈的眼鼻旁已空出；下杆现在在更高的额缘由头后露出，仍有贴额上缘的观感，**不称完全避开额头**。请Astra/Opus以同区前后图裁定是否接受此后方遮挡。没有扩散到后续曝光，也未批量重渲。

`CAM20_actual_same_palm_axes_4x.png`可核原掌/玉镯与两条刚性轴。`verification.json`核CAM20、灯、房间、曝光/fog、人物配准、龟装配与两龟杆端点、鹤偶姿与原part/at/固定夹点逐字段相同；`zero_call_provenance.json`及像素mask核人物/玉镯与非杆非指缝域RGBA变化0。本轮图像工具调用0，正式渲染1帧。

复现准备：父目录 `prepare_cam20_raise_002.py` 读取本包保留的geometry_preflight作已选单一根位计算，再 `node .../check_and_render.cjs --render`；不需要也不允许全片或旧Blender。
