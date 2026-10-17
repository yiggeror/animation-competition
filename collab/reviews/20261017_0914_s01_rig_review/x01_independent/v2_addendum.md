# x01 最终头部边界修订独审

**结论：新版可交 Opus 作 S01 限定试接。** 原 1431 稿的“左辫下黄肩误归 head”静态阻断已修正，撤销为该污染而要求 head 固定的限制；这不代表头部动作或蒙皮质量已经通过。首次头动仍只能作为作者保守范围内的待测试项，须看引擎实帧。

唯一接入文件：`/tmp/laidian-s01-rigs/revision_head_v2/x01_prone_phone.rig.json`

SHA256：`48650432c05c4b6d1af4882fc76a157f7867863b3a65ca671aaeb222b8cadaa7`

已实际查看作者 `head_braid_effective.png`，并独立按 regions 首个匹配顺序将新范围栅格化回原图：此前可见黄肩块已排除，发梢凹口保留，剩余极少边缘色点不再构成黄衣块随头运动的问题。新 head 多边形无自交。只比较本次变化：除 regions[1] 边界与 notes 外，骨、其他 regions、pins、eyes 等与 1431 完全相同；15 个交付文件 hash 与新版 manifest 一致。

静态证据：`head_v2_review/region_01_effective.png`、`head_v2_review/head_revision_check.json`。旧 1431 报告及其图、JSON 保存在 `1431_review/`，未覆盖。

原审查中的其余限制继续适用：隐藏髋/远膝仅代理；没有隐藏 thumb 或独立按屏能力；phone 和双掌共享静态刚体区域；pins 是网格权重固定而非 IK；腕/膝/发梢边界和半闭/全闭遮罩需实渲；未进行本次 S01 动态或正常速度观感验收。新引擎已修的独立层 pin / keepUnder 逻辑问题维持关闭，不作为此次数据阻断。

本轮仅此边界复核，不扩大动作或美术范围，未改作者、仓库或原素材。
