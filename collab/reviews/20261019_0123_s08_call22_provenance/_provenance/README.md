# S08 F049 / call22 来源保全

唯一 call22 原始 request、完整 prompt、五实际输入及 raw 原样保全。最终母图 8f03f271d52c35283e0be68ab7146004a81c2f0231ccbab85f198524916c7bd1。累计 22 张真实图、23 次工具提交；其中历史 1 次参数校验产 0 图，call22 仅 1 次提交/1 张 raw。

实际五步：固定配准 nominal 回贴 → semantic_v1 手腕重建 → measure_material → 软色 → 封三层。measure_material 生成软色脚本实际读取的 MATERIAL_SAMPLES.json，不能省略。register_raw.py 保留来源，精确复现使用冻结参数，不重跑优化器。nominal/semantic 是同 raw 采用链中间态，不计新生成或虚构失败；不上传这些重复整母 PNG。

整个变换后近根 2451 像素须下次重接；硬域含 AA 6709、最近邻原核心 6609。独立前景对平母差 255（核心 254）如实保留，实际 frozen source-over 基线差 0，不能将平母裁片冒充独立前景。原近根 2383、源硬域 6611 仅为变换前来源数。6440 白域外零变，1860 旧空气黑域无复活；远手历史 150、完整 AA 159、当帧可见子集各自保留。

新腕上沿仅白域内局部平滑提高最多 8px，非整臂平移；软色只新腕亮面 G+3/B+1，共 2750 像素，alpha、腕褶/下侧转折不变。亮面 sample2 相对 000 的均值 G -4.2386、B -4.0915 如实保留，不能改称全样本 ±4；形体暗面仅诊断。

ROWS.json 含真实 local、完整仓库 path、sha256、gitsha、bytes；OBJECTS.json 供按 blob 复用。7 个前态读取依赖用 EXTERNAL_DEPENDENCIES.json 引用既有 7700a641 来源，不重复封 046。REPLAY_SEED_AND_CLOSURE.json 明确最小冻结 seed，生成候选/最终母/层/mask 只作退出后 oracle，不预种。只读检查见 READ_ONLY_CHECKS.json；隔离实跑作为独立四文件补充，原 GAPS 保留当时状态。

finalize_metadata.py 及其最终合同/收据/状态另按原字节保全；五步重放不执行台账副作用，不声称产生最终人工签署 metadata，详见 METADATA_SEALING_BOUNDARY.json。

作者原件、prompt、raw 均未改；无生图、仓库和网络写操作。最终封层 QA 大图与全部运行产物不重复打包。
