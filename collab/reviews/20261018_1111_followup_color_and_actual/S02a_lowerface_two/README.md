# S02a F023/F044 下脸冷影一致性候选，尚待独审

只做两张，底图是已交的显式颈领修复候选，未更新任何既有final或仓库。目的在于保留本镜邻态原有脸内冷影的一致性，不表示全角色底色完全中性，也不表示实际视频切换已通过。

## 先看
- qa/neighbor_source_before_after_comparison.png：两组邻态原源 / 目标原底 / 局部候选 / 邻态原源。只用于源画局部比较，不是新MP4。
- qa/S02a_F023__before_mask_after.png
- qa/S02a_F044__before_mask_after.png
每张为底图、实际渐变mask、候选，并带较宽脸部视图。

## 范围与方法
各自从真实黑下颌线封闭的脸域内取mask，不用近白或肤色颜色分类。嘴线下方y708之后才开始渐变；F023的有效支持框为[720,709,950,754]，F044为[713,709,959,759]（坐标含端点）。嘴/眼/鼻及y≤708逐像素不变。

F023参考focus和tense原态，F044参考F041和relief原态。参考色度先在各自真实脸域做归一化平滑，依嘴/颏位置及每行脸宽映射色度分布，然后平均两侧参考。只映射色场，不移动任何底图像素。渐变使用零起止斜率smoothstep；下颌边界只向内羽化1.5px，黑线原样保留。每个底图像素的亮度保持，RGB取整最大亮度差不足0.482/255。

## 验证
两张已实际查看前后图、邻态比较页及渐变叠图，未见平蓝块或明显涂脸硬边。当前冷影仅缓和下颏跳色，是否足以消除实际切换观感仍需独审。

独立检查：mask外RGBA、全部alpha、原嘴眼鼻、黑下颌、已修颈和左右领均0改动。frozen_replay_check.json确认冻结色场重放与候选SHA完全相同；源/候选/参考SHA和坐标参数见candidate_validation.json。

## 复放
候选：candidates/*__lowerface_cool_candidate.png。
冻结mask/色场：masks/内binary支持域、8-bit渐变预览、真正应用的局部float64 NPZ。
执行：python apply_frozen_chroma.py --base-dir /path/to/prior_semantic_neck_collar_candidates
底图必须是先前颈领候选，文件名S02a_F023.png、S02a_F044.png；工具校验SHA，输出到本包replayed/。不能使用未经颈领修复的原件作底。

build_lowerface_candidates.py记录色场推导过程；交接优先用已检查的冻结NPZ复放。无生图、无镜头表改动、无其他镜头批量处理。
