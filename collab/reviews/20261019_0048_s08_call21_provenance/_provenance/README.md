# S08 F046 / call21 来源保全

唯一 call21 原始 request、完整 prompt、五实际输入和 raw 原样保全。最终母图为 7722c85545660ae240acc72d512985572b1a5ba5532780b150b4b8274c385ec2；a6ccf172…69441 保留为已批准软色中间态与初封层历史。

实际采用链：固定配准与 nominal 回贴 → 自足 v9_base → v9_cloth → v10 接口 → 显式域验证 → 软色 → 初始 a6 封层 → 显式 233 旧空气轮廓清理 → 最终 7722 封层。233 mask 必须由初始 a6 层与实际前景外扩 2px 推导，不能从已清后的最终层反推；这不是全局 alpha 阈值清理。旧 233 点逐 RGBA 同 043，其中 NO_ROD 223 点透明、10 点旧施工带；恰 233 点归零，域外零变。三层互斥、原 RGB、逐 RGBA 重建一致。

1.110666 为肘腕端点投影比；局部中心线切向约 1–1.19328，横截面宽度系数 1。胸袖新增 7633 域、前臂新增 349 域、最终几何 union 107303 均保留。近手仅 6611 真远端硬复用；全部 2383 近根下帧须重接，独立前景与平母直接差 67、已知下垫回合差 57，不能称为纯取整误差。远手历史 150 / 完整 159 / 本帧可见 147 分开保留。

ROWS.json 指真实 local 与完整仓库 path、sha256、gitsha、bytes。OBJECTS.json 可按 Git blob 去重；EXTERNAL_DEPENDENCIES.json 复用前包已有 F043 对象，不重包旧三态。ROWS_POST_CORE.json 排除已交核心 15 路径。封层 QA 大图、重复历史 PNG 不上传；原 seal manifest 中仍保留这些产物的来源 hash。

REPLAY_RECIPE.json、DEPENDENCY_GRAPH.json 与 REPLAY_SEED_AND_CLOSURE.json 给出九步、34 个最小 seed 和精确读取依赖；本任务未执行 F046 重放，只做静态闭包和只读像素核查。GAPS.json 保留这一真实缺口。HISTORY_BOUNDARIES.json 列 v1–v9 历史与已知原因，不编逐版缺失回执。原始图、prompt、作者脚本均未修改；无生图、仓库或网络写操作。

累计 21 张真实图、22 次工具提交（历史 1 次参数校验失败产 0 图）；F046 仅 1 次提交、1 张 raw。版本数不计为调用数。
