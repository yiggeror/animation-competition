# S22 唯一首F000，实际原件交Astra锁母审查

沿双审通过的`1e63ae70828ca965645e042f225200eddadfa32e`，本批实际图像调用1次、返回1张、工具失败0次。只画F000，未画012/024或整批，未改公共场景/曝光/音轨/ready。

- [未改原始输出](originals/F000_call01_raw.png)：1672×941 RGBA，SHA256 `57f14bae2b0e48cf35e0270f7d7384e28719897282bd1ff02b036ec429e52353`。未抠边、未清理、未校色、未注册或挪动手指。
- 实际alpha叠底：[灰底全图](qa/F000_raw_on_gray.png)、[白底全图](qa/F000_raw_on_white.png)、[夹签/空气隙2倍局部](qa/F000_contact_gray_2x.png)。仅用于实看，原像素/透明度未改。
- [完整实际prompt](provenance/F000_call01_prompt.txt)、[实际请求](provenance/F000_call01_request.json)、[原返回来源](provenance/F000_call01_tool_metadata.json)、[输入SHA](provenance/input_SHA.json)。
- [角色色彩基准来源及采样](provenance/role_color_sources.json)、[实际取样对比](qa/observed_color_check.json)、[原件/轮廓检查](qa/raw_file_checks.json)。

已实际看原件、灰/白底及放大夹点：奶奶右手在后上方近而未触，无镯；小满右手独立握一根主签，近面拇指甲、与远面食/中指之间的暗缝可读，腕/掌/弯指连续。alpha≥128的两主连通轮廓独立，最小距离19.21原始像素。未把此距离当三维间距或Astra锁定结论。

色基使用奶奶current03和小满v4原手像素，未使用旧h22四色手或施工图棕肤色。角色取样G=(254,210,177)、X=(254,205,171)；返回所选掌面样本G=(253,204,165)、X=(253,202,163)，略暖，未擅自校色，交Astra判断母态色彩。没有画死的手电斑或场景光。

透明RGB预览中可见杂色散点；实际离散小连通块最高alpha6，灰白真实叠底不见明显斑块，原件保全未清。结构、色基及后续是否同raw清理均由Astra审首图后锁母；本包不自行宣称生产采用。
