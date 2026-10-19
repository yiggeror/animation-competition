# F046 / call21 九步隔离重放

9 步均 exit 0。34 个冻结 seed 起步，未预种任何 F046 中间图、最终母、层或输出 mask。仅 validate_v10_geometry_union.py 的一个绝对根路径字面量替换；算法、prompt、raw 均未改。原版九脚本另存 original_scripts/，完整原件已在来源包。

最终母 SHA：7722c85545660ae240acc72d512985572b1a5ba5532780b150b4b8274c385ec2。
三层 SHA：
- body：81c054b8e846d168947914b01c6e50f7faee4415dc3d959a7a0c91d67cc53128
- arms：c2bfe5faa0ffb431e451742b84481c469fc288f31ae0856429e6be6089400263
- table_box：c5f43dfae8b43b8436a2f67a5a013a77509ea049b1c798d501bdfbe8083bf984

187 个生成产物中 181 字节相同；171 个 PNG 全部字节相同。余 6 项仅 4 个 JSON 的绝对根路径，以及 2 个 seal manifest 的路径与引用 JSON 的 hash/bytes 传播；两份 manifest 的文件清单一致，零内容/像素差。三层互斥、原 RGB、alpha 求和与逐 RGBA 合成全部通过。冻结来源 123 路径复核零变化。

执行时 audit guard 禁止作者树访问、网络和源脚本派生子进程，并限制写入独立重放根；9 步无禁止操作尝试。最终母/层只在所有子进程退出后读取作者原件作 oracle，不复制它们作为重放结果。此次不运行可选 ffmpeg 六帧 QA。

来源包历史 GAPS 的“未实跑”已由本补充关闭；先前对 manifest inventory 差异的预估没有发生。历史提案文件名 PROPOSED_233_semantic_old_air_contour.png 不属于最终清单；采用的实际 CLEAR233 mask、其公式脚本与来源回执已保全，且重放精确产生同一 233 mask。

只提交四个小文件：本 README、replay_entry.py、RUN_EVIDENCE.json、COMPARISON.json。RUN_EVIDENCE 包含全部九步 stdout/stderr、文件 IO 记录、34 seed hash、原脚本 hash 和唯一根路径 diff。COMPARISON 包含全部 187 产物逐项 SHA 与完整六项差异。生成 PNG、全部工作树和本地日志不重复提交。

再次执行：在同一工作根的新空目录放 replay_entry.py；旁边保留已封 astra_s08_call21_sources_20261019_0048 清单及其真实 source local。依次运行 python replay_entry.py prepare、python replay_entry.py run、python replay_entry.py compare。prepare 拒绝复用已有 worktree，并只建必要空输出目录；compare 强制等待九步成功结束。原始来源包保持冻结，不覆盖其历史 GAPS。
