# S08前20帧 · 新增014/017实际接景

固定`6f73473a8230ed7a1b236f32605e622769d29109`，入口`collab/reviews/20261018_1800_s08_first20_scene/s08_first20_scene.js`，SHA256`16d77bc7ff1b3356030c7ba374502acedf62015239f82a8a231667f75a354a50`。按指定原命令加现有shim真实渲染：[实际MP4](S08_first20_1920x1080_24fps.mp4)，1920×1080／24fps／20帧／20/24秒／无声。仅000–019，未渲020及后段；非整镜ready。

**旧前14帧全部沿用：**[无损Canvas逐字节比较](prior14_exact_comparison.json)先核原PNG等于2383f9f既交SHA，再与新20帧的000–013逐字节比，14/14相同。没有重复整理旧图/眼态证据，也没有拿不同GOP的有损解码作相等依据。旧眼态沿Astra澄清：006约1/5眯缝、009部分回开、012全开，未要求完全闭眼。

新增实际查看[013/014/016/017/019解码](00_requested_incremental_decodes.jpg)、[手盒与桌面](01_hand_box_table_actual.jpg)、[盒底4倍近图](02_box_base970_actual4x.jpg)、[双臂/肘与前唇](03_both_elbows_front_lip_actual.jpg)、[柴头火源](04_match_fire_actual2x.jpg)，另实看017原尺寸Canvas。014仍托着盒、盒随远手下降；017盒在原桌面只出现一次，原托举位置无第二盒，手指自然落到盒右侧。近臂/肘在前唇前，远臂按原新态抬起，轮廓没有被前沿横切；不把017抬高的远肘说成仍压在桌上。

**盒底微影实际可核：**[真实Canvas开影/关影诊断](05_box_contact_on_off_ACTUAL_CONTROL.png)及[像素差](contact_actual_difference.json)只在浏览器内临时去掉盒contact，没有改源文件。诊断的采用17/19重渲与主20片源PNG逐字节相同；去影后对照分别有50/51像素变化，均落在y970一行，x范围1062–1142以内，最大RGB暗化约21/13/7级，无亮向变化。影紧贴盒底，在原桌面950.2–981内，未越前唇981，也没有脱离的一块浮影。它是极薄贴底暗线，不夸大成明显大面积投影。`diagnostic/`两张无盒影图仅作对照，未用于采用MP4。

[源层核验](box_source_validation.json)确认盒1665个alpha像素仅在独立table_box，body/arms无重复；alpha>128最低行970，盒层只画一次。固定新15层/模块/helper/背景/tools均同Git原字节，旧10层原字节相同；本次没有重新分层或改图。014/017真实柴头仍在(1074,782)，近柴火和暖光未跳到盒或手心，灯罩未动、灯芯无火。[合同及诊断运行记录](contract_and_diagnostic_runtime.json)保留所有20帧pose/fire；只用纯`frameAt(20/24)`核缺口抛错，不对020调用render。

`decoded/`仅保留指定5张1920×1080实际解码PNG。[全20帧编码核验](actual20_validation.json)逐帧核主片与Canvas源次序，最大RGB通道MSE9.503；[ffprobe](ffprobe.json)确认帧数/时长/无音轨。全部20张无损源保留于本工作区`build/S08_first20/`。近图都只是实际帧裁切放大，未补画盒影或人物。

[执行命令与环境](run_manifest.json)、[渲染日志](render.log)、[解码日志](decode_check.log)、[盒影诊断日志](contact_probe.log)及`tools/`齐。渲染唯一404为原favicon，无JS页面渲染错误。完成固定源检查后回原独立分支只提交本目录；生图、生产模块/原图/机位/灯/声音/EDL/ready写入均0。新增两态/薄影原速主观复审交Astra，不扩大到后续整镜。
