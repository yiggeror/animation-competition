# S10 第一阶段 · 参考冻结提案

当前状态：**9097b275修复母态已获Astra锁定；F024／F027／F030顺链三态及实际33帧实景前缀已完成，交Astra审后再开033。** 最新三态取图与实际曝光见 [F024_027_030/README.md](F024_027_030/README.md)。累计图像请求6次：母态及衣带2次、本批4次（含027首版质量退回1张）。033及后段未生成。母态原件、必要修复完整保留于 [F000_first/](F000_first/README.md)、[F000_repair/](F000_repair/README.md)。下面保留第一阶段参考说明，技术构造图不能用作成片人物。

基线 `3d66443997cee24b64059e6f53f7d46968a3a05c`；已包含交办时的 `118cb8cb`。独立分支 `collab/cloud-s10-reference-20261018-1324`。`collab/claude.md` 最新明确指示为 13:50 的合成分工；本包仍先交参考，Astra 统一整合并维护 ready.md。没有修改共享留言、实现、EDL、音轨或其他镜头。

建议依次看：

1. [八态同机位总览](reference/01_eight_poses.png)：120 帧／24fps／5 秒。快转 3 帧一张，8 张独立新画。
2. [实际身份图的比例及关节标注](reference/02_observed_proportions.png)：奶奶表情02、三视图03；旧 g10 只取造型，不继承其固定眯眼或歪头。
3. [整头和颈部三关键](reference/03_whole_head_neck.png)：0°→22°→32°，含颅体、鼻向、双耳遮挡、眼镜、低盘发与连续颈面。
4. [层次及接触接口](reference/04_layers_contacts.png)：近臂／躯干／远臂三档；本镜双手、双肘、手腕全在画外，不添加挡光手势。重点接触是眼镜鼻梁／耳挂、颈根／固定领口。
5. [曝光与绘图说明](drawing_brief.md)、[结构化曝光表](S10_plan.json)、[CSV](S10_exposure.csv)。每态单图见 `reference/poses/`。

构图提案：全镜固定 1920×1080 头肩近景，发顶和盘发完整；机位沿用旧代码后段的近景方向，取消其前 72 帧全景／后 48 帧特写的分切。原因是新版清单明确写近景，5 秒需要读出实际转头。旧接触表只证明左侧手电、右侧马灯、原时长与景别，不作为动作依据。此构图变化须随参考由 Astra 冻结。

第一阶段提出的三个接口：①全镜近景及八曝光；②画右约32°偏头＋约6°侧倾、颈根固定；③F022光先达脸、F024收眼，光在场景层。Astra已据8f129821允许启动首F000，原文在 `F000_first/provenance/freeze_authorization.md`；后续仍逐门审实际图，不能由此把整链标为通过。当前只交首图原件；锁000后再继续027／033等关口，保留前一张合格原件，不以未锁首张批量派生。

环境：仓库和绘图参考处理工具可用；`image_gen.imagegen` 已于F000实际执行成功。第一阶段确为0调用，得到单张启动冻结后才执行本次1调用；没有借测试调用提前生成。未启动 Blender、全片渲染、付费服务或外部图像 API。之后 S10 专用模块候选与实际1280×720／24fps自查，按新授权在真实画稿完成后另交。

来源和未执行提示词在 [provenance/source_manifest.json](provenance/source_manifest.json)、[prompts/README.md](prompts/README.md)。技术图由本包 `build_reference.py` 从人工测点与明确标记的三维构造生成；不是生成模型的原始输出。第一阶段没有生图原件；本次F000完整实际请求、输入、未改原件、工具返回及检查均另存 `F000_first/`，PLANNED提示词仍保持历史草稿身份。

本包可复跑：在仓库根运行 `python collab/reviews/cloud_s10_20261018/build_reference.py`。不需要安装依赖、渲染项目或联网。

补充委托的已完成 S03a 实渲协助另见 [render_assist/README.md](render_assist/README.md)：固定f4f0ea43模块原样渲36帧，交720p／24fps无声MP4和实际解码九帧接触表；不涉及S03a生成或模块修改。

第二次补充委托的已完成S05a完整实渲见 [render_assist/S05a_README.md](render_assist/S05a_README.md)：固定5c454750模块原样渲60帧，交720p／24fps无声MP4和实际解码14帧。未改S05a模块或音轨。

排队S07两段诊断已完成，见 [render_assist/s07_partial/README.md](render_assist/s07_partial/README.md)：固定60159846只渲000–024与039–056（25＋18帧），交实际MP4、解码24张与日志；缺口未渲，不当全镜完成。
