# S05a 有效前五态：显式颈领mask局部候选

仅包含仍有效的F000/F010/F014/F024/F028。旧F044/F046/F050/F052_v3已撤回，不在此包中；此前两张示范输出完成但未独审，只在本机另处归档，停止使用。

## 内容
- candidates/：5张RGBA局部候选
- masks/：每张独立左领、右领、颈binary及soft可视化，共30张
- source_manifest.json：5张原件固定SHA和本机来源
- semantic_mask_validation.json：逐张参数、候选SHA和像素断言
- independent_pixel_check.json：独立重新核原线稿封闭域、原像素及不变范围
- qa/valid_five_review.png：五态原件/mask/候选及脸部保留图
- build_semantic_candidates.py：默认使用冻结binary mask；源SHA不匹配停止

## 验证与使用
逐张打开原件及mask前后叠图。5张各自提取的黑线封闭三域，均与已通过的S02a focus mask完全一致；每个mask内源RGBA也逐像素等于focus。F028与focus的其他差异仅到y700，不进入颈领mask。F000候选文件与已通过S02a focus候选字节完全相同。

5张alpha、mask外RGBA、暗线保持；肩顶与轮廓不移动，脸/下颏原像素不变。颈领分别保留原像素亮度，只去掉其局部偏色，未将阴影刷平。亮度差至多0.5/255，仅输出取整。

复现：python build_semantic_candidates.py --source-dir /path/to/originals
原件目录内使用5张原文件名。依赖Pillow、NumPy、SciPy；脚本仅写自身目录。soft PNG是8-bit可视化，精确应用权重由冻结binary mask的距离变换重算。

不要再对这三块运行旧的全下半部颜色分类。候选仅通过局部像素验证，不等于脸下颏去偏色、实际MP4或场景光通过。未改仓库、镜头表、时长，也未生图。
