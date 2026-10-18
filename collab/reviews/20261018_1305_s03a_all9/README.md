# S03a 全九曝光静态交付（校色锁版）

独审通过九态与下脸 color_v2；candidates/ 为本包唯一生产取图目录。1672×941 RGBA、24fps、36f、1.5s。000×8 → 008×3 → 011×3 → 014×3 → 017×4 → 021×2 → 023×2 → 025×3 → 028×8。

14/25是视觉中间态，不冒称精确15°；17/21/23是继续真转开的视觉峰态，可能强于设计30°。17经整头下移22像素及最小颈接修复，身体肩领全锁。21/23仅自由尾端继续/回落，头脸颈发根与17精确一致。25复用14体积、28回原focus体积，微闭撅嘴保留。

14/17/21/23/25在静态原色基础上只校准语义下脸RGB；掩膜外与alpha均零变化。原色副本在 original_color/，此前17/25/28原色交付仍保留，现取本包校色副本。原始生成、显式拼接掩膜和完整prompt保留在主工作目录；尾端本包另含真正生成供体、形变/源坐标与脚本。

qa/ 内原曝光24fps MP4、九态同机位及回程表已导出，编码只在最底补1背景像素。前景手瓜仍由Opus单独前景层承接，未烘入人物。此包通过静态画与锁像素核查，未称实片自然度通过；真实场景接入、手瓜遮挡、转幅节奏与最终色光仍须增量审核。

累计13次builtin image_gen，工具失败0，质量拒用4份原件保全。本包无任何新增生成调用。详见 manifest.json、SHA256SUMS、qa/ 与 color_provenance/。

## 协调交付追加
九态角色隔离36f实际解码门已独审通过，证据qa/S03a_all9_actual_isolated_color_v2.*；MP4只作角色曝光诊断，无前景/真实场景/音轨。完整上游原件在固定提交 f796cb4e6420b6b2b2e779103dd7fa7b853aa524 的 collab/reviews/20261018_1221_partial_drawn_candidates/S03a_first4/，以及45527936cd7cd2f3dd089b6aabef4bb062566852的collab/reviews/20261018_1251_pose_bases/S03a_peak_return/。本包新增尾供体与校色mask，取本包candidates不要混用旧暖下脸。

### 脚本边界
可直接运行 `python render_candidates.py` 验九锁SHA并重建角色隔离36f到verification_replay，不改候选。协调发现作者三个工作脚本依赖原工作目录、原色候选/诊断目录等，已移入scripts/archival_working_directory_only，仅保全过程，不把它们宣称为本薄包独立一键重放。不要对已校色candidates再次校色或运行原尾端构建覆盖。
