# S07 F057 同原图分区回母色＋完整近踝语义清尾

唯一新候选：[F057_semantic_color_and_ankle_PENDING.png](candidate/F057_semantic_color_and_ankle_PENDING.png)，1672×1080 RGBA，SHA `93939f3e148c0a957ef418c677e60cc3fd27cf6b6844f91d500c8a3508b76720`；[原配准世界图](candidate/F057_semantic_color_and_ankle_world_PENDING.png)。本轮生成0，S07累计仍3次／3原件，在途0。完整保留6a6e269的真实call03原件、prompt、返回和生成记录。

已由作者与既有云6.1sol实际看[灰底](qa/full_body_and_materials_gray.png)、[深底](qa/full_body_and_materials_dark.png)及[完整踝语义前后图](qa/whole_ankle_before_after.png)，未见新增明确结构或颜色阻断，可交Astra整态锁定评审；本包不自行宣称Astra已锁。

执行本轮[原指示](provenance/parent_instruction.txt)，源为6a6e269候选 `1b166dc6…e7919`，G037固定生产源 `4ebf2dc0…ac4f8a`。14°完整臂、短步、裤根连接、全部配准与轮廓保留。G037仍原朝向，只作同材颜色取样，未镜像拼身。

| 材料 | 本轮完整权重区RGB修正 |
|---|---|
| 脸 | −10／−8／−9 |
| 耳 | −8／−3／+3，单独实测回母 |
| 颈 | −10／−19／−23，单独实测回母 |
| 近臂 | −6／−12.5／−21.5 |
| 远臂 | −5／−8／−14 |
| 双手 | −3／−8／−22 |
| 蓝衣 | +18／0／−23 |
| 裤料 | 仅B−6 |

各皮肤区域平滑相接；蓝衣另域，低亮墨线与中性灰影退出；裤仅蓝通道小修。完整白花及其AA、眼镜白框、灰发、玉镯、踝皮、鞋底均保源RGB／alpha。没有把各部差异当成全图同一偏移。[头部实测前后／母源](qa/actual_head_parts_palette_before_after_mother.png)及[取样记录](qa/head_parts_actual_palette.json)显示额颊修后距对应母源各通道约0–2，耳颈对应中值同；像素色阶匹配不代物理光照重建。

近踝按完整裤脚→踝→鞋后口x760–882/y938–980实看，仅清伸出真实后跟的旧斜线尾至汇合处：36个有alpha像素（其中alpha>128为16），实际清除域x775–791/y967–974。主裤边、踝肉、真实鞋口和底保留，alpha域外0变化，没有用窄框横切一整条线。

[repair.py](repair.py)可从固定源重放；[checks.json](checks.json)、分部权重mask、完整硬保mask、[独审记录](qa/61sol_actual_review.md)及SHA清单齐。除旧尾36点，alpha逐像素不变；双鞋底仍native y1022、世界774.874，未改支撑或重新摆姿。颜色改变域内仍保线稿的形状与原灰影层次；这里的硬保数值检查指文件中明确保存的中性／深墨及材质保护mask，不夸称所有带色细线均逐RGB固定。
