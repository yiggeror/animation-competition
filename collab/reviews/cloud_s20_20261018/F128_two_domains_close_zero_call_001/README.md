# F128 两域收口，0 新图调用，待 Astra 实际门

- [正常完整候选](actual_full_gray_1x.jpg)
- [120 左 / 收口 128 右，同尺头胸](120_left_closed128_right_same_canvas_head_chest_1x.png)
- [正常双掌接真实有限杆](CAM20_F128_true_finite_rods_both_palms_albedo_1x.png)；[夹口 3×](CAM20_F128_true_finite_two_grips_albedo_3x.png)
- [原 CAM20 单张实际接景](CAM20_F128_current_branch_actual.png)
- [候选 PNG](F128_two_domains_closed_CANDIDATE.png)；[候选 SHA](FINAL_PNG_SHA256.txt)
- [保留原候选](source_d240ffae_UNMODIFIED_candidate.png)；[实际差异](actual_changed_pixels_mask.png)；[两授权域](two_authorized_domains_mask.png)

仅处理 Astra 对 `d240ffaecd878f04f5591815e6b341356f257702` 批准的两域。0 新图像请求、0 新原件，保留本次自身原生惊讶神态、抬视和后收，候选尚未采用；未开 132、未冻结曝光。

**掌外旧导向：**只清除两掌外原生绘制短导向及 L 掌下自由短尾。完整原生掌指腕臂受保护，像素变化为 0。真实接景仍使用本轮已定有限 A→B，端点、轴向、长度和龟偶根位均不变，没有靠缩杆或挪掌掩盖。正常实图单夹关系可读，交 Astra 判断；不把此前 L 的 10/13 圆帽采样单独当作接触失败。

**自身整头体量：**先排除马尾、花、呆毛和下颈作主颅/主发实量。120/128 的主颅宽比 1.14365、高比 1.18590、面积线性比 1.12134，主发宽比 1.15470、面积线性比 1.12077。眼耳连线角度随抬头改变，不用其单个距离比驱动五官缩放。以五项线性指标的对数中位数取 **1.143646408839779**，对本次头脸、全发、花统一恢复；没有拿 120 头替换或分挪五官。

围绕本次实际颈根 `(649.6744,384.0465)`，不另加旋转/自由平移。下颈在实际弯曲领口上方 28px 连续衰减至原位置，保留领口与原生衣身。头颈自身提取包含原头透明边缘，避免把旧头边缘当固定衣身覆回，颈口不带衣料孤边。

收口后主颅宽与 120 相同；高度仍差约 3.35%，面积线性指标约大 1.9%，保留两态投影差。主颅冠顶相对 120 的低落从 39px 降至 12px，本次衣领根本身比 120 低约 14.37px，因此没有为硬追同一屏幕头顶继续抬头或拉长脖子。

完整原生衣身双臂整裙、固定完整下肢支持、奶奶均保留，保护域像素变化为 0。C 层几何未改，只随新头轮廓改变可见遮挡。只渲染 F128 同一帧；首遍检查修正提取 AA 后重查最终单张，共两次局部单帧计算，没有全镜/全片渲染。

来源和前后实量：`measurements_before.json` / `measurements_after.json`；保护证据：`repair_and_protection.json` / `VERIFICATION.json`。复查命令：`python verify_and_crops.py`，不调用图像或渲染工具。
