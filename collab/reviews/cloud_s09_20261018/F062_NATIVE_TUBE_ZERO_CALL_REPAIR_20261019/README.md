# S09 062原生筒面零调用最小接回

按Astra最新实看：060完整头裙接回已通过；062前置刚性尾盖正确，原native062在拇指/滑键之间确有连续真实筒面。本包仅采纳该块真实材质，062仍交Astra主审，不自行锁态。

最终候选：`candidate/F062_NATIVE_REAL_TUBE_AND_KEY_IDENTITY_PATCH_PENDING_ASTRA.png`，SHA256 `a301035e87678f51ac44b09099ee6696c28648da847f043b1ef99ccf67f6882a`。同位置单材质采纳4577px，bbox[1025,502,1168,627]。材质注册M=I、t=[0,0]、s=1；原whole-raw统一770/1145+[550,0]保持不变，未另拟合、拉长筒身或移动手。原生键面完整采纳，采纳域跨过旧孔裁切边/AA，已清原斜黑切线与重复键边。不是仅填alpha0洞而把旧边留下。

先看 `qa/F062_ACTUAL_NATIVE_before_after_local_dark.png`：同尺native实际材质／修前／修后。完整两臂、刚性尾盖与头裙见 `qa/F062_full_actual_repair_dark.png`。原完整掌指RGBA变化0、已知真实外轮廓保护区0、材质域外0；采纳像素对native062同位置RGBA差0。灯头/前端y<490和新尾盖/下臂y>=640全图变化0。未重抽原raw顶部或整灯，没有创建RGB或alpha去补洞。

实际短曝光：`exposure/S09_F060x2_F062x1_F063x6_gray_ACTUAL9f_24fps.mp4`，深底同名dark片。060×2→062×1→063×6，共9帧、24fps、0.375秒、无声。原1672×941绘图不缩放，底部仅加31px QA条。灰/深各实际9帧均解码准确分类；实际换张和完整握手/迎掌/尾盖近图在qa/ACTUAL9f_decoded*。作者已实际查看，完整场景和最终流畅门交Astra，不以像素保护代替动作审。

几何、源commit:path/完整SHA、材质域和保护结果在 `geometry/exact_source_patch_and_protection_checks.json`。最新060已锁/062待审的2态替换索引在 `geometry/S09_060_062_latest_source_overlay_PENDING062.json`，其余96帧索引仍沿1460bc6d。所有列明源已从指定git对象核SHA。原始062工具返回、完整提示词/冻结输入/未改raw仍在10262cd1的 `F060_F062_NATIVE_from_APPROVED6940a80f_20261019/F062/`；本包新请求0、新原图0、重试0，不重复打包旧证据。

可用 `repair_and_expose.py`复现本次真实源像素接回及9帧编码/解码。原生产代码、其他镜头和共享文档均未改。S07末8帧按最新协调指示尚未启动，等待alpha-only接地影源新固定提交。
