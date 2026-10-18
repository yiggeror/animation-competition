F079修正单张交付：作者与6.1sol独立静态完整体量均通过，待Astra锁定。

准确源4e25e5f07a8aa86926634b21b9f5884f547cbb10，仅request_RELATIVE_NOT_CALLED.json指定3图与原文prompt，字节和SHA均核实，未附旧073或失败079为工具参考。源包原字节保全在frozen_astra_input/。本次修正1请求/1原件；F079累计2请求/2原件。

唯一候选：`candidate/F079_corrected_complete_volume_PENDING_ASTRA.png`
SHA `856d10c9516c33a8e992a121033e76a5ac55bda269b16949a90aa431206f0364`。
唯一新原件：`originals/F079_corrected_call01_RAW.png`
SHA `38b9ea55ebead05cae142d2ee911c88528f600c11dfbb5d65c02c8cada1c808a`。完整提示词、工具参数/含base64原返回、host路径均保留，base64=host=archive逐字节同。

先看`qa/F079_corrected_layered_crop_gray_TRIAL.png`、dark对应图和`qa/F079_corrected_actual_connections_gray_TRIAL.png`。实际近右腿低膝浅屈，小腿近向下接前落原踝，远左腿后撑且在近腿后；整腰臀/胯裆/双膝/双裤口为这次原生完整新画，不拿源参考的行投影、腰片或技术接缝当画稿。实际两裤口自然接原踝，腰衣下无浅带/大透空，原双鞋sole均1022。隐藏关节proxy仅近似方向，不冒充实骨测。作者实看记录见`qa/root_actual_complete_volume_review.json`。

原生1024x1536只作整幅均匀0.5078125注册至520x780，裁窗900,280,1420,1060。从实际原图抽完整裤料82352px，428个返回的非裤材料以显式mask排除；没有代码肢段变形/新画或接桥。固定原上身/双整臂/双真鞋5层SHA全同，六生产层可逐RGBA重放候选0差。裤色对锁057均值(+0.51560,+1.40569,+2.90177)，对062(+0.26930,+1.53335,+3.27550)，均各通道≤4，无RGB修正，保原阴影/墨线/alpha。

`compose_corrected_complete_volume.py`为无网络/无新生图的完整图层重放；`sources/source_snapshot_manifest.json`为本包原来源。未开后态或曝光。本单张先交Astra，S09后段仅读精确帧表/现有锁图，不改唯一锁052/056。

独审记录：`qa/independent_61sol_corrected_review.json`。根作者隔离新目录重放的候选PNG原字节一致，目标成品未作为计算输入，见`qa/isolated_replay_verification.json`。仅单态静态门，不是动态/整镜通过。
