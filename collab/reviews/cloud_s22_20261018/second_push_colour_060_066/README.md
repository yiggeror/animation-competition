# S22第二推：同原图有限修色，待Astra复审

第二推结构已双审可保；依 [本次明确修色指示](provenance/authorization.txt)，在 `6d2ad21e513ae90a87706d017df82a217cbfab56` 的060/066同尺绘图上，仅修指定新前臂颜色。原生图、原提示词、前一同尺版均保留原字节；没有追加生图、重画、重新映射或改位移。024同截面中明面为主参照，042辅助，未强行把新绘前臂全部拉成相同RGB。

[060修后RGBA](candidate/F060_colour_fixed.png) SHA `356c67d7c62efe46b4e68bece873407571adbc994801a622c39db2fdb1bfc136`；[066修后RGBA](candidate/F066_colour_fixed.png) SHA `849de1cf2633d3818c59c73e5a68f22cca77a24c9fce8d44bce7b005385c1d60`。均1672×941。

先看 [060：024／修前／修后同尺度](qa/F060_024_before_after_native.png)、[066：同尺度对照](qa/F066_024_before_after_native.png)。三栏均为原尺寸相同裁切，未缩放。修色沿真实前臂从固定入口到腕前连续展开：x<400为主体，400–520平滑收至0；随明暗和边缘距离减弱，不是整臂统一加减。060只孩子近侧前臂，中明面G−1～2、B−2～3，成人全部不动；066成人中明面仅B−2～3，孩子B−3～4，G−1仅落在相对024同截面有绿色余量的局部。暗部、最亮部、轮廓附近及柔收段剂量更低，R全图不变。

| 同截面中位样本 | 成人RGB | 孩子RGB |
| --- | --- | --- |
| 锁024主参照 | (253,209,175) | (254,205,171) |
| 锁042辅助 | (253,208,175) | (253,208,173) |
| 060修前→修后 | (253,209,177)→不变 | (253,210,177)→(253,208,174) |
| 066修前→修后 | (253,210,180)→(253,210,177) | (253,209,179)→(253,208,175) |

取样仍为原尺寸x250–350、各真实alpha截面中部5像素；[完整样本](provenance/same_section_measurements.json)。只做获准小幅修正，保留源图渐变。各臂修前后亮度相关性均≥0.99978，未用新的光照或整臂平涂替换原明暗。

全部alpha、x≥520整接触群、指甲／腕褶／夹点／单签，以及轮廓墨线及其2像素保护带，均逐字节一致；另保护真实轮廓内3像素带及alpha<240像素。原图内部常有253/254的alpha，保留原alpha，只修其内部RGB。060成人0像素变更。固定入口和累计位移(+37,−21)/(+49,−28)完全保持。[逐项保护与通道分布](provenance/correction_checks.json)附原像素SHA；[独立复核](provenance/verification.json)再次检查五处锁024接触区域、入口和位移。

[色mask目录](masks/)含16位连续权重、真实上下两臂语义分区、墨线保护区及实际改动区；`actual_subtraction_RGB_x60`是实际减色量的60倍可视化，不是角色稿。灰底mask叠看：[060](qa/F060_mask_overlay.png)／[066](qa/F066_mask_overlay.png)。完整浮点权重、原图截面及实际有符号RGB减量见各`provenance/*_colour_masks.npz`；[可复现修色脚本](repair_same_drawings.py)保留所有阈值与边缘、明暗、纵向柔收算法。

[060–083修后24帧曝光](S22_060_083_colour24.mp4)为1秒，[000–083修后84帧前缀](S22_000_083_colour84.mp4)为3.5秒；均1280×720、24fps、无音轨，标明“隔离曝光（非实景）”。前六态逐SHA沿锁图，仅060/066换为本次修后版。逐帧解码比对全部持帧边界正确，并实看切换整图和 [24帧解码缩览](qa/S22_060_083_colour24_decoded.jpg)、[84帧解码缩览](qa/S22_000_083_colour84_decoded.jpg)。24帧片本地0–5对应S22的060–065，本地6–23对应066–083。[视频SHA与信息](provenance/delivery_manifest.json)。

原始来源链：[060原生图](../second_push_060_066/F060/originals/F060_call01_raw.png)、[066原生图](../second_push_060_066/F066/originals/F066_call01_raw.png)、[060完整原请求](../second_push_060_066/F060/provenance/request.json)、[066完整原请求](../second_push_060_066/F066/provenance/request.json)、[来源SHA清单](provenance/source_manifest.json)。本次图像工具调用0次，累计仍9次尝试／8张成功原图。旧绘图及旧小包未改；曝光CSV、计划JSON、生产模块、EDL、音轨、ready与共享文档均未动。待Astra修色复审与最终实景，084仍暂停。
