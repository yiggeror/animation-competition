# 最小候选 patch（未应用）

交付：`s18_minimal.patch`（82 行 unified diff）、可读候选源码 `patch_candidate/`、构建记录 `build_patch.py`。

**没有修改仓库。** 在主仓 `427132bc50d98f8d54171c916f722900b5fc26ac` 上运行 `git apply --check` 成功。S18 patch 以该版重新冻结的 `patch_base/js/lamp/shots/s18.js` 为基础，保留 Opus 最新 `T_PU=0.58`；没有覆盖新时间表、剧情或骨架参考。原 `report.md` 对旧时间表的计算绑定 `932a5f4`，是历史阻断证据，不能继续当作最新计划。最新整数帧/三位小数转换由另一审查者核查。

改动范围：

1. flip JSON 必须显式给 `canvas: [635,1175]` 与 `referenceAnchors: [[x1,y1],[x2,y2]]`。两点是**母版中的静止特征**，每张的 `anchors` 是对应源图点；第一张也做变换。不会再暗认第一张就在母版坐标。
2. 验证 canvas 正整数、锚点两有限点且间距至少 1 px、frame 文件存在字段、timeline 从 0 开始且严格递增、frame index 整数且在范围内；已加载三图的尺寸必须一致。manifest HTTP 错误保留状态。
3. S18 的审核入口为页面 `?flipReview=1`，或在首次渲染前 `const shot = await import('/js/lamp/shots/s18.js'); shot.setFlipReviewRequired();`。此模式下加载失败会抛出带原始 cause 的错误；即使之前已缓存 legacy null，开启审核后也会抛错。普通未启用模式保留原旧片行为，不能用它交付试点。

没有改 timeline 的秒单位语义，没有替换为整数帧表；Opus 接最新整数帧计划时应从整数 `f/24` 生成时间，不要依赖不精确的小数或期待此 patch 自动修正时序。没有增加角色图、补间、法线向量旋转或 Alpha 越界自动修正。缺法线/材质的现有平图 fallback 仍允许，交付时须报告实际采用路径。

浏览器对照：`node probe_patch.cjs` → `patch_probe_results.json`。

- 同一非母版首张，旧版得到自身 160×100、锚点仍 (70,10)/(70,25)；候选得到显式目标 100×80、两点精确落 (20,20)/(50,20)，实际 Canvas 像素非空。用小画布只是探针；生产 target 为 635×1175。
- 缺目标/画幅、退化锚点、越界索引、逆序时刻、非零起点、错尺寸法线共 7 类输入均明确拒绝。
- 合法输入在 `n/24` 的 72 次采样均有效。本项用单色块单 key 验证基本路径，**不宣称已有 12 图实际片**。
- 原失败缓存 `null` 在显式审核模式下转为错误，原始 `fixture missing keyframe` 原因保留；未假装输出新片成功。

待真实新图到达，仍须测每帧实际锚点、变换后的头/手/衣服与凳脚、Alpha 边缘和完整 72 帧合成。此 patch 的通过范围是上述有限程序行为，不是自然动作验收。
