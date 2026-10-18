# F031连续裙外缘接回 · 0生成 · 交Astra整态锁母

唯一原生坐标交付图：[F031_raw_clothing_and_contours_for_final_lock.png](candidate/F031_raw_clothing_and_contours_for_final_lock.png)，1672×941 RGBA，SHA256 **`4b59c62485cf382c3e2d411de3c8ca9fb4edee622dad31b41946362889d44da7`**。另有[原配准图](candidate/F031_registered_for_final_lock.png)及[720灰底全图](qa/F031_1280x720_gray.png)。原曝光、相机、配准、已过双手／整筒／尺寸与净空不改。

先看[灰底修前／同位供体／实际接回](qa/continuous_contour_before_donor_after_gray.png)和[深底对照](qa/continuous_contour_before_donor_after_dark.png)。作者与[6.1sol只读复核](qa/cloud_61sol_actual_review.md)均已实际查看两张对照及全图：旧左突出残片、右下界缺口已消失，两边连续到画底，内部白点与裙褶接续保留，未见新增可见接缝阻断。这里交最终031静态锁母审查，不代替Astra确认，不提前派037／042。

严格执行固定 **`f17651aaee6f03cf0e48bd2939c4c6c1fb86cffb`** 的[连续走廊mask](source_reference/continuous_skirt_outer_edge_allowed_REFERENCE.png)与[逐行合同](source_reference/corridor_contract.json)，旧两小矩形限制已撤回。左从raw y820、右从y840连续到940，8146px许可域；仅从保留call05**同位完整RGBA**复制，不缩放、不移位、不画纹理。本次RGBA改变3682px，其中alpha3168px；走廊外RGBA／alpha变化均0，完整双臂／手／整筒／头颈变化0，旧硬保护域除明确释放走廊外变化0。两边alpha128轮廓逐行等于供体，相邻行最大步长均1px，上接y820／840改变0。详见[执行检查](checks.json)与[全行轮廓坐标](qa/continuous_alpha128_edge_rows.json)。

[build_delivery.py](build_delivery.py)可重放：先核源 `db697c53…f73714`、供体 `05b3301d…f1ac93c`，逐行mask与许可PNG一致后执行，并断言全部锁域。固定提交的参考原文件、原代码及各自SHA原样保存在[source_reference/](source_reference/source_manifest.json)；历史失败包、原始生成返回和提示词不覆盖。

**新增生成0，S09累计12次／031累计7次不变，037／042均0，无请求在途。** S07保持原分支等待其远腕技术门，本包未混入S07文件。
