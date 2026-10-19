# S20 000–035：实际36f曝光候选

`actual_F000_035_36f_24fps.apng`：按原曝光表12项覆盖36f/24fps，精确1.5秒。已接入原生Astra004（3b3ea25f，PNG SHA1ffad3ca…425661b8）及fa47c63d的012/015短尖、022腕接清理；三修仍待Astra增量审。018复用020稳定骨相/轮廓，只保留裙内褶变化，不算新独立姿态。

同尺近图 `..._contacts.png`、全身表 `..._fullbody.png` 已实看。`external_decoder_verification.json`记录独立ffmpeg解码36/36帧与曝光表指定实图RGBA完全一致；源路径/SHA及每帧曝光见manifest/CSV。新增图像调用0、004云端调用0、整景渲染0。高鹤CAM20候选另外交，不把它未审的杆角批量传播到此曝光。

`build_review.py`保留可复现合版；原生004原文件与源README按原字节保存在 `native004_source/`，来源提交/原路径/全SHA齐，未改对方目录。
