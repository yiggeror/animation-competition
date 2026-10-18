# 031两条外缘限定接回 · 新增生成0，边界仍需Astra裁定

先看 [灰底两ROI对照](qa/two_ROIs_before_donor_after_gray.png)、[深底两ROI对照](qa/two_ROIs_before_donor_after_dark.png)。各行依次为修前、call05同位供体、严格限定框接回。原图 [F031_exact_two_ROIs_NOT_LOCKED.png](candidate/F031_exact_two_ROIs_NOT_LOCKED.png)，[720图](qa/F031_1280x720_NOT_LOCKED.png)。这是一份短包，不重整旧失败记录。

严格按Astra批准的raw含端点坐标：左x618–630/y829–846、右x968–981/y843–856；对应Pillow排右下框 `[618,829,631,847]`、`[968,843,982,857]`。共430px释放域，直接取保留call05原件**同位完整RGBA**，无缩放、移动、画纹理或生成。实际RGBA改变303px，其中alpha269px；ROI外RGBA与alpha改变均0，其余原硬保护域改变0，双手／整筒／头颈完全保留。累计S09仍12调用、031仍7，037／042均0。

**实图没有过“接顺”门，不能锁031整态。** 批准矩形截断了连续轮廓：左y838修后首个alpha>128像素x623，y839仍有框左界外x617残片，约6px突出；右y856修后最末像素x981，y857落在框外，仍回缩至x973，供体该行应为x982。灰／深底均能看见，不能用“文件已生成”代替通过。作者与既有云端6.1sol只读实看、独立扫描结论一致，见[复核记录](qa/cloud_61sol_actual_review.md)。

[checks.json](checks.json)记录源SHA、候选SHA、逐ROI变化及上述行坐标；[build_patch.py](build_patch.py)可独立重放并断言锁域。原3e8ffa4候选与call05原件均未覆盖。等待Astra按实际边界裁定允许释放的连续轮廓范围或其他连接方法；本包未擅自扩框、改框外alpha或派037／042。
