# 031衣片语义域／同raw接回候选 · 先交Astra审

**新增生成0。** 先看 [三处实图对照](qa/three_semantic_regions_comparison.png)、[完整语义域](qa/full_semantic_domain_overlay.png)、[720候选](qa/same_call05_1280x720_pending_review.png)。三行分别是胸口截断白点、旧臂腾空躯干／腰片、连续裙褶；每行依次为当前031／唯一call05同位连续衣片／接回候选。6.1sol独审后已补整掌包络硬保护，避免肤色分类漏卷指小岛；候选PNG逐字节不变，见`qa/cloud_61sol_actual_review.md`。

[联合mask](masks/semantic_clothing_union.png)明确包括胸口，三份独立语义mask及`crops/`内逐区原图／供体／候选／mask均齐，不再只给裙部两条。[硬保护域](masks/hard_protection_all.png)涵盖头颈领口、完整双臂肤色链及袖口褶边、整手电、真实外轮廓7px保护带与背景。肩袖白点仍在完整袖片保护区，本次未动，不把衣片修复扩大成改臂许可。

接回方式：只从`../originals/d06_call05_raw.png`同坐标取连续衣片RGB，不平移、不缩放、不画纹理；当前031全部alpha原值保留。候选`candidates/same_call05_continuous_cloth_pending_review.png`仅改变语义联合域内43754个RGB像素。新画全人／手电均无调用；旧七次031原件不变，037／042未画。

[覆盖与锁域检查](qa/coverage_and_lock_checks.json)：胸口mask1925px、躯干腰片19218px、裙褶55034px；mask与硬保护交集0，硬域／mask外／全图alpha变化均0。作者已实际看三处及720图，胸点和主裙褶已连；硬边附近衣纹接点仍交Astra裁定，**此候选未锁031整态**。

[build_preparation.py](build_preparation.py)重建全部语义crop、mask、同源候选及检查。源为fa749a9d当前031与保留call05，固定路径／SHA见检查JSON。若同源接回仍有缺口，再沿经审mask作一次局部衣片补连接；本包没有提前调用。S07在此包交审后沿G037精确源继续，不并发生成。
