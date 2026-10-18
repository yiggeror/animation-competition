# F057定向连接1次 · 原件与最小重组交Astra锁母审查

**Astra已通过本图身份／结构／短步与裤根，指定仅同原图语义回母色与近踝旧尾清理；最新完整修复入口为[分区颜色／踝尾](../F057_semantic_color_ankle/README.md)，SHA93939f3e…8b76720。本文原候选及计数保留为历史。**

**唯一当前候选：[F057_call03_minimum_connections_PENDING.png](candidate/F057_call03_minimum_connections_PENDING.png)**，1672×1080 RGBA，SHA256 `1b166dc6e0ba1367eec70544c80bd690abab643299c85e9a317d1e64c1ce7919`；[世界配准图](candidate/F057_call03_minimum_world_PENDING.png)。先看[三处修前／实际重组](qa/three_connections_minimum_before_after.png)、[全身灰底](qa/F057_call03_minimum_full_gray.png)、[全身深底](qa/F057_call03_minimum_full_dark.png)。[6.1sol实际复核](qa/postreturn_cloud_61sol_actual_review.md)未见新的明确几何／拓扑阻断，同意交Astra锁帧审查；颜色门仍待裁定，**尚不冒称057整态已锁**；其他10态未生成。

执行固定 `56cb80c3dca135a1dbc6acde378433259590a183` 的14°完整臂与批准语义包络，旧623腕目标已撤回；同源短步64／真实鞋底775预摆不重做。既有6.1sol实际看最终crop/mask后才发一次局部原生请求，记录见[预调用实审](qa/precall_cloud_61sol_actual_review.md)。裁图为原画布 `[560,300,1080,1045]`，520×745，排除头脸，只请求远袖→肘→近端前臂、裤根与近踝必要接续，没有请求整人或新姿态。

**实际调用本轮1次，S07累计3次／3原件，当前采用仍0，在途0。** [原始返回PNG](originals/F057_call03_raw.png)，1047×1502，SHA256 `d0dab9f994ac1337ff0aec9cc50c6e779a3c355370c10f9a59e16b39db8e3d11`，已核工具返回base64、宿主PNG与归档PNG逐字节同。[完整参数](requests/F057_call03_arguments.json)、[完整prompt](requests/F057_call03_prompt.txt)、[完整工具返回](requests/F057_call03_raw_return.json)、[冻结输入及审查](requests/F057_call03_freeze.json)、[执行状态](requests/F057_call03_execution_state.json)均保全，不重复调用。

返回只作整张crop等比0.4966571156配准，无分段缩放。整白域直接取回会带入侧衣提亮、新裤褶／矩形边和小悬弧，因此保留该诊断，但**不要采用 `raw_locked_PENDING_REVIEW`／原世界图**。当前最小重组只用冻结14°源、已对齐的唯一原生返回，以及同场call02母图同坐标591px裤料来封闭裤根；不画新颜色／轮廓，不加新肢体。裤根指定盒179个旧透明点已全部封闭；侧衣原底色／阴影保留，多余悬弧恢复源透明像素。

近踝初始操作mask曾把裤脚低饱和AA／空孔误判为脚料并膨胀保护；独审确认定位的38点全在原e93踝语义域内，域外0，允许纠正误分类并零调用重组。现用**原完整鞋／踝片段按原变换重放后的真实alpha材料**作保护。修订采纳域比初始输入mask多254px，实际多改192px，全部在原获批踝域内；未修改冻结输入或伪称初始mask外0。当前批准语义采纳域外变化0，完整真实鞋／踝皮、鞋底、镯手、头与近右臂变化0。见[最小重组检查](qa/minimum_recomposition_checks.json)及两份分别保留的输入／后采纳mask。

**颜色门需明确裁定。** [实际底色／暗部对照](qa/material_shadow_fill_actual_comparison.png)和[材质／接地记录](qa/material_and_support_actual_checks.json)分开取样：G037站姿母源底色约(246,189,141)，冻结057近臂已为(252,202,163)；当前局接远臂约(251,196,156)，更接近G037但并非精确同色。此亮粉基线差并非本次局接才产生，未越权重染已保护的头／近臂／全衣。亮度分组只作图像色阶对照，不冒称物理光照拟合。双鞋实图alpha128底缘均y1022、世界774.874，踝横距64；这不是动力学稳定证明。

[review_call03.py](review_call03.py)核全部冻结输入与原件后重放初始诊断；[recompose_minimum.py](recompose_minimum.py)重放最终取回与保护断言；[material_and_support_review.py](material_and_support_review.py)只读量核。来源56cb全部参考文件原样保存在[source_reference/](source_reference/source_manifest.json)。本包未触碰S09；S09的031已由Astra另行锁定，037／042随后独立推进。
