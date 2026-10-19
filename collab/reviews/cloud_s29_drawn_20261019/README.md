# S29 首母输入准备 · 待Astra短审 · 生图0次

新分支 `cloud/s29-drawn-reference-20261019`，基于实际读取的最新生产提交 `9172ef0798383badf7af337eb91c49b6a63415f8`。本包只写此独占目录，保留S07/S09成果；不生成、不改生产/EDL/音频/共享留言，不新建云任务。已有6.1sol仅在原会话只读看输入。

先看 [01完整首母技术目标](inputs/01_FIRST_MOTHER_COMPLETE_TECHNICAL_TARGET.png)，再看 [04完整双臂与接触](inputs/04_COMPLETE_ARMS_AND_CONTACT_TARGETS.png)。这是带真实旧身份像素和原生产皮影的技术参考图，**不是新原生画稿或已采用首母**。新的完整人物、双臂/掌指和自然软布仍须在放行后画一张实审，不把旧人物拼图或网格布面冒充成品。

本次首母提案：奶奶坐凳、略俯身、低头小小闭口笑；布仍在双膝上打开，两偶及四根真实接点直杆都留在奶奶处。近右裸腕手扶鹤neck3区域C1，远左带镯手捏抬起的布沿C2；C2层次明确为手指→蓝布沿→尾羽→下层布→双膝。原生输出须把真实指腹/拇指夹布和扶偶接触画出来，软圈/旧手像素并非接触验收。网格只示支承平面，须画成自然不透明棉布。

五个实际输入：

1. [完整目标](inputs/01_FIRST_MOTHER_COMPLETE_TECHNICAL_TARGET.png)：头、双臂、布、两偶、双脚与凳全见。
2. [身份／真实材质](inputs/02_ACTUAL_IDENTITY_MATERIAL_ONLY.png)：旧原件脸发、衬衫、左镯及靛蓝印花棉布。
3. [原生产皮影／布面支承](inputs/03_REAL_PUPPETS_OPEN_CLOTH_SUPPORT.png)：调用未改的makeCrane/makeTurtle及rig真接点，四杆直；整个偶同一膝面投影，不拉单部件。
4. [整臂／接触与前后层](inputs/04_COMPLETE_ARMS_AND_CONTACT_TARGETS.png)：C1/C2的实际完整上下文，留给新手指画稿复核。
5. [实际现代码机位](inputs/05_ACTUAL_CAMERA_LIGHT_ONLY.png)：仅渲t=0一张1920×1080，无整镜重渲；只参考现机位、亮度、空间。原始未标注Canvas PNG在camera/CODE_CAMERA_ONLY_F000/。

**最新明确指示优先。** 已读collab/README、claude/partner末尾、现剧本与已批准清单。Opus在`372d96fe79e4bb090e5589ebef664c890cf67912`明确“S28、S29都不交签”，奶奶把鹤、龟一起包；交龟省略到S30→S31，S31首张半开布包可见。原文保存在[sources/OPUS_372d96fe_EXACT_DECISION.txt](sources/OPUS_372d96fe_EXACT_DECISION.txt)。现剧本“小满仍攥龟签”及旧代码turtleLayer不能盖过这条新裁定。

旧20261017 g29及试点仅作身份/材质/坐姿支撑来源；不继承旧AB8.1–8.42、抬头冻结、六态时表、F240回退或clothDisplacement/triangle掰动作。当前只有一张首母设计；S29仍为12秒/288帧、约36态的原任务，没有制定新全时表、追加镜头或生成小满手机回看。

人物比例/完整臂链及当前机位映射见[软参考几何](geometry/proportion_camera_AND_scope_SOFT_NOT_BONE_LOCK.json)。袖下肩肘为肉眼估计，明确不是骨长实测；首母实际返回后才量本镜统一骨长与自然透视，不强贴旧结构错误。原偶真接点、四直杆和布层次见[接触几何](geometry/soft_target_and_true_prop_contacts.json)。

[完整提示词准备稿](prompts/FIRST_MOTHER_PLANNED_NOT_EXECUTED.txt)和`prompts/arguments_PLANNED_NOT_EXECUTED.json`均未提交。本轮仅输入准备，等待Astra短审及明确放行首母生图；没有在途请求、原生新图或“原始输出”可伪记。原旧身份图的实际prompt/request/tool metadata和完整原图SHA以源commit:path保全在sources/SOURCE_INDEX.json。

来源、所有输入完整SHA、读取回执、机位实际资源日志及有限实看结论均随包保存。当前机位静帧和技术图均已实际打开检查，供Astra快速审这张首母输入；不等待全36态。
