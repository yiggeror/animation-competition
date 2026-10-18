# S08首23帧 · 高初位灯杆与020离盒实际接景

固定`d6071b76c8b069c7112134320a69058b896ff1f5`，入口`collab/reviews/20261018_1828_s08_first23_scene/s08_first23_scene.js`，SHA256`26d3a8aeb40a9208040ff04c8535a450585330ca596076f0f16294191ae77cc7`。按指定原命令加现有Chromium shim真实渲一次完整23帧：[实际MP4](S08_first23_1920x1080_24fps.mp4)，1920×1080／24fps／23帧／23/24秒／无声。只覆盖000–022，020×3；未渲023及以后，未另外重渲旧20帧。

已实际查看[000/013/017/019/020/022解码](00_requested_actual_decodes.jpg)、[019→020完整双臂与离盒](01_leave_box_whole_arms_actual.jpg)、[空掌与高杆间隙](02_empty_palm_high_rod_actual2x.jpg)、[真实柴头](03_match_true_head_actual3x.jpg)、[桌盒与970底边](04_table_box_base970_actual4x.jpg)，另实看000/020原尺寸Canvas。000起就是新高杆；020空掌已离盒向杆，腕/肘/袖链条可读，指端仍未接杆；近手火头随原画(-12,+5)到(1062,787)，不跳到手心或灯芯。灯罩保持未抬、灯芯全段无火。本包不把到杆前的准备态当成扣杆/压杆完成。

**旧实帧只差灯杆：**[旧20/新23实际无损帧对照](05_old20_new23_lever_actual_comparison.jpg)直接取保存的旧000/013/017 Canvas PNG，先核SHA等于69d2e31证据，再与新23帧对应PNG逐像素比较。[差异JSON](old20_lamp_only_difference.json)记录1165/1167/1166个变化像素，实际外接框均`[1233,730,1305,836)`；按原/新杆几何包络授权ROI`[1225,720,1315,845)`外变化0。没有拿有损解码比较代替源帧，也没有重渲旧入口。

**盒仍承在原桌面：**020盒alpha及可见RGBA与017逐点相同，1665像素只在独立盒层，body/arms无重复；盒底alpha>128最低行970。[源核验](source_validation.json)保留18层及固定模块/helper/局部灯JS/背景/tools的Git字节检查。实际[开/关盒影对照](06_box_contact_on_off_ACTUAL_CONTROL.png)仅浏览器内临时省略盒contact，采用020/022诊断重渲与主23源PNG逐字节相同；[像素差](contact_actual_difference.json)分别65/60像素，都只在y970一行，未跨前唇981。它是薄贴底暗线，不扩大成明显大面积投影。`diagnostic/`两张无影控制图未用于采用MP4。

`decoded/`保留指定6张原1920×1080实际解码。近图均为实际帧裁切/缩放，未画人物或补影。[全23帧编码核验](actual23_validation.json)逐帧对应Canvas源，最大RGB通道MSE9.473；[ffprobe](ffprobe.json)确认规格与无音轨。完整23张源在工作区`build/S08_first23/`，旧20源仍保留。合同/诊断[运行记录](contract_and_diagnostic_runtime.json)核23帧pose/fire，纯`frameAt(23/24)`抛错，未对023调用render。

[原命令与环境](run_manifest.json)、[主渲染日志](render.log)、[解码日志](decode_check.log)、[盒影诊断日志](contact_probe.log)与`tools/`齐。主渲染唯一404为原favicon，无JS页面渲染错误，证明本地shell/Chromium实渲可用；此结果不宣称S24图像服务恢复。固定源检查后回现有独立分支只提交本目录，生图、源模块/图/相机/灯具/EDL/音轨/ready编辑0。原速自然度与后续动作仍交Astra审，本包不是完整S08或声画ready。
