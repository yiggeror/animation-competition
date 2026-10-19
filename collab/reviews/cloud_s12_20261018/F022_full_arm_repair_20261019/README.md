# S12 F022 单次远臂修复｜失败停机

严格使用 a72d5231 最终门批准的冻结 prompt/request，**实际调用 1 次、返回 1 张**，未重试；S12 累计 7 次。原生 1024×1536 RGBA 输出确实是完整远臂，但整体放大、移位，未遵守冻结注册。**不接受此 F022，F026/F030 继续不绑定。**

- [工具原件](originals/F022_far_arm_patch_call01_raw.png)：SHA `6e87f65ad06119f6483ba02bbfa072117f7fc1dcc32e4c79b374b67e7e41d543`，与工具默认输出逐字节一致，未移动、缩放或修指。
- [原生位置与可改域](review/returned_patch_vs_approved_domain.png)：实轮廓 alpha≥128 的 87.00% 落在批准远臂域之外。[严格域内复合诊断](review/REJECTED_exact_domain_composite_DIAGNOSTIC.png) 保持域外失败022像素完全相同，却无法接成肩袖—肘—腕链；该图明确不作成品。
- [真实冻结道具诊断](review/actual_props_returned_patch_DIAGNOSTIC.png) 与 [无损10倍接触图](review/actual_contact_DIAGNOSTIC10x.png)：按原定 `.70+(275,112)` 注册，拇指在上签左侧未首触，其他指已与上签相交；alpha≥128 的臂手像素与真实上签相交 249 像素，下签相交 0。原件及接触近图已实际核看。报告中的人工拇指邻域 ROI 只提供保守间距，未冒充精确语义或骨测。

[完整实际工具参数](provenance/actual_tool_arguments.json)、[原冻结 request](provenance/frozen_request.json)、[精确 prompt](provenance/exact_prompt.txt)、批准记录及工具返回路径均已保全；冻结 request SHA 仍为 `2d0339d05f7eb315e8be0a7a880012f1b6668c6b2b30b09b05085392256c3a6d`，prompt SHA 仍为 `bbd7296c8d51c1e72a1f2dcf87bfa92b901b0677b44756a25c244e931d339805`。三张实际输入继续引用同分支前包的冻结原文件与 SHA，未替换。

[检查结果](review/SELF_REVIEW.json)、[调用账本](provenance/call_ledger.json) 和 [诊断复现脚本](tools/build_review.py) 齐全。本包只有静态来源像素复合，场景渲染 0；没有改双签、箱、鹤或布，没有改共享实现／留言，没有后续调用。
