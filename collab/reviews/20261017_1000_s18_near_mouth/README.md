# S18 近口实际诊断片与透明图接入修正

**可直接看的产物：** [带说明的四次重复版](near_mouth_clip/near_mouth_repeat4_titled.mp4)，24fps、36帧、1.5秒、960×1280、无声；[原始单段](near_mouth_clip/near_mouth_9f_24fps.mp4)，24fps、9帧、0.375秒、636×1176、无声。标题已明确“近口三态诊断，非完整S18”。

实际输入只有两张新生成图与一张既有捂嘴母版，顺序v2→v1→母版，每态停3帧。原版只为偶数编码右/下各加1px灰边；使用独审提供的635×1175相似配准诊断图，合成阶段没有重配准、缩放、裁切、局部变形、补间或叠化。完整[逐帧清单](near_mouth_clip/manifest.json)记录原件/配准图哈希、矩阵、输出帧索引及编码命令；9+36帧均全解码检查通过。为避免重复收录相同停帧，本包保留三份输入、实际MP4和三个解码关键帧，manifest里的逐帧散图路径是原运行目录记录。

原始段SHA256 `e62275feba317d86426d3259a050a00fa54cca08451eaf9ca91fa51d88824db7`；带说明版 `df0398f158b1cbdbcf59d93b9ba57744854c45331f7b3a8d534643a106de8ceb`。

这段仅供双方实际看片判断近口姿势切换；**没有从膝盖抬手、喷笑起点、偷瞄/收尾，也没有完整三秒S18。** 两张实际图仍未执行目标低肘姿势，头/领口变化仍保留，未用制作手段掩盖。主审实看实际编码的F0/F3/F6，未声称实时原速观影或自然表演通过。两图完整独审、提示词与原件见[上一批](../20261017_0946_s18_first_trial/README.md)。

## 560e261接入实测

[独立报告](compositor_560e261/report.md)与浏览器探针确认：新整数表72次采样正确，F15喷笑、8/9三循环、F45/F54/F63后段均对，旧舍入项关闭。

两张922×1706原件到母版需要约0.689缩放，实际loader被0.8下限拒绝；先统一分辨率且同步锚点后，实际load+flipMaps成功。可采用保留原件与变换的规范化方案，或把名义像素比例与剩余形变分开。不要把正常分辨率转换当姿态/造型失败。另补齐二维锚点结构与整数frame index校验。

新flip_manifest工具对同一被loader拒绝的原件也会exit0写mode:flipbook；因此必须核实际渲染路径与加载日志，不能仅凭静态清单字段。manifest不存在仍会走旧片，正式试点不能用这个路径冒充成功。

## 已实证并给出修正：透明图不得重新按RGB抠背景

当前prep_flip无条件cutout，而cutout先convert RGB丢原Alpha。用本次v2实际运行，原透明像素中10116个被转成明显可见，凳下/腿内/鞋底出现红黄杂边；[左原件、右重抠实际对照](alpha_preparation/original_left_recut_right_stool.png)。这和先前正确Alpha合成无杂边的结论不冲突，损坏来自后续重抠。

[最小候选补丁](alpha_preparation/prep_flip_preserve_alpha.patch)：已有透明RGBA直接复制，再运行card_maps/card_soft；旧不透明输入保留原流程。没有应用你的源码。root在隔离完整pipeline实际运行后，固有色字节与原件一致，三图922×1706且Alpha逐像素等于原件；[结果](alpha_preparation/corrected_result.json)、[报告](alpha_preparation/report.md)、[独立复核](alpha_preparation/independent_note.md)。`git apply --check`在当前主仓通过。这只修数据处理，不替代姿势/灯光/运动验收。

下一步请先保真接入并看此短段，反馈实际姿势切换与领口/头部是否可接受。没有足够证据前，我方不追加k04或其他镜头关键帧，不把两张近口候选改名成既定k06完成，也不继续抽同一张碰运气。全片旧批渲仍冻结。
