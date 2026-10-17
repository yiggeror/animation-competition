# S01 骨架试点审查归档；主线已转 S18 关键帧试点

**状态：归档，不是请继续推广骨架。** 交付前读到 Opus `b9bc99d`、`5dc508f`、`81b78a5` 转贴用户否定奶奶六秒样例、选择 S18 三秒关键帧试点并要求骨架参考。父线程也要求核实该转述、对齐后再做小范围验证。因此本批只保存已完成工作，S01 绑骨不再扩量、不要求因本包恢复主路线。

## 已完成的实际检查

- [奶奶动作独审](g01_motion/report.md)：实际六秒 600×1000、24fps/144 帧片，头和手有局部连续运动，但同一豆/豆荚始终在手，不能算完整剥豆。盆区域误纳绿镯下缘：四个探针 100% 绑盆，而腕最多移动 16.64 原图像素，实际 F7/F22 镯子拉伸。[帧证据](g01_motion/wrist_bangle_actual_frames.png)、[坐标候选](g01_motion/g01_coordinate_suggestions.json)。候选未采用、未复渲。
- [奶奶脸部独审](g01_face/report.md)：已交六秒片双眼全程睁开；另以冻结 66ea5f7 代码自渲六张眨眼帧，确有眨眼，但 F22/F23 全闭时两眼上缘残留眼白。[六帧条图](g01_face/acts66_blink_selfrender/eyes_blink_strip.png)。两组来源分开，不把旧视频当最新 S01。
- [三项引擎修复实测](engine_fixed/report.md)：942df5d 的尺寸 A→B→A 返回同一实际画布、像素一致，无 GL/页面报错；keepUnder 保留 body 网格；独立层默认 root pin 权重为 1、漂移为 0，见 [独立消费者复验](x01_independent/consumer_reproduction_fixed.json)。这些具体缺陷关闭，不代表蒙皮自然或遮挡补洞问题解决，也没有审过 renderMaps。
- [字幕修复采用核验](caption_fix_adopted.json)：Opus c08b572 采用 expansion=none；除新增注释外，实际代码与已实跑恢复 S02/S05 百分号文字的候选一致。

## x01 已完成数据，仅归档

[最终 JSON](x01_archived/x01_prone_phone.rig.json) SHA256 `48650432c05c4b6d1af4882fc76a157f7867863b3a65ca671aaeb222b8cadaa7`，17 骨、8 regions、8 pins、2 眼候选、layers 空；源图原生 1536×1024。手机背面遮住拇指，没有虚构 thumb 或独立按键能力；phone 与双掌共享刚体。

[作者说明](x01_archived/author_report.md)、[原作者 manifest](x01_archived/manifest.json)、[最终独审补充](x01_independent/v2_addendum.md)。黄肩误归 head 已修；旧 1431 报告保存在 [历史目录](x01_independent/1431_review/report.md)，不得把旧限制当新版结论。作者 manifest 的 pending 状态是冻结时原记录，后续独审以 v2_addendum 为准，未改写原报告。未做 x01 动态试片或原速自然程度验收，归档不等于请求采用。

## 新试点的当前边界

S18 现有十二张 k01–k12 是母版加骨架参考，不是生成完成的角色关键帧。先核骨架、源图尺寸、时间表、稳定定位点及合成器；统一 11/12 张歧义和 8/9 复用时间，再做限定关键帧一致性试验。已完成代码机制或静态骨长检查不代替普通画面观感，不提前生成其余镜头。

另请保持 S31 当前“开镜已亮、母带已去 click”，新 motion-plan 的“0.6 推亮”与此冲突，须修计划防回归。S18 的噗时刻也正按现行母带核对。

本批无新 AI 图片生成，未改 Opus 实现或留言。逐帧视觉审查不等于实时原速观影或听审。部分原始脚本保留执行时绝对路径和快照身份；本包 manifest 是打包文件的真实哈希，原审查 manifest 仍用于来源追溯（其中逐帧散图未重复收录，以完整联系表覆盖）。
