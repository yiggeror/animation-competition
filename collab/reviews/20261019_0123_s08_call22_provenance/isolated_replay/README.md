# F049 / call22 五步隔离重放

5 步均 exit 0，29 个冻结 seed 起步。完整原版脚本未改算法或根路径；未预种任何当前 F049 候选、母图、层、生成 mask 或收据。执行顺序：固定配准 nominal → semantic_v1 → measure_material → soft color → seal_handoff。输入来自来源包 ROWS SHA 50124437952eb8daeeb79c31c4d0dad6f73caa1cefead8d902d1d3972e3d7551。

终母 SHA：8f03f271d52c35283e0be68ab7146004a81c2f0231ccbab85f198524916c7bd1。
三层 SHA：
- body：3c0b077e660433faeac31011a767cfa3a1756a559fb285bd43205e325a707a99
- arms：047e5506eede0cd7f7a9bfff6fef0a2e9e869e9b2d0aa252e514a6b42da6827f
- table_box：82411d00da844aaac638ab1e79adb197741a2b06146b0a9caac3433333370e74

83 个生成产物中 79 字节同；74 PNG 全部字节同。三层互斥、原 RGB、alpha 求和及 RGBA 重建均通过。其余四个差异如实保留：独立手 source-over 审计 JSON 仅绝对根路径不同；合同与层验证存在后置最终审批字段差异；manifest 还有最终审批字段、引用 hash/bytes 及单独 SOURCE_RECEIPT.json inventory 差异。不是把所有差异统称为纯路径。

按协调边界，本次不执行 create_initial_source_receipt.py / finalize_metadata.py，不复制 ledger/formal-plan 前态，不假造初始收据或最终签署。上述脚本、准确最终合同/收据/状态已在来源包保存。当前五步确实重建了终母、所有三层及独立前景/保护档；只未生成另行封门的 SOURCE_RECEIPT，且未声明重放了最终台账 metadata。

所有 oracle 图像均在五个子进程退出后读取；执行 guard 阻止作者树访问、网络与源脚本派生进程，并限制写入独立重放根，无阻断事件。封档 105 路径再次读回全部不变。原版五脚本另存本地 original_scripts/，其完整原件已在来源包；不重复上传输出 PNG 或整个工作树。

只提交四文件：README.md、replay_entry.py、RUN_EVIDENCE.json、COMPARISON.json。证据包含全部五步 stdout/stderr、实际文件 IO、29 seed hash、完整逐产物对比与上述 metadata 差异。它关闭原来源 GAPS 的图像重放未执行项，不覆盖历史文档。

复跑：同工作根另建空目录放 replay_entry.py，旁边保留 astra_s08_call22_sources_20261019_0123 与其真实 local 来源。依次运行 python replay_entry.py prepare、python replay_entry.py run、python replay_entry.py compare。prepare 拒绝复用已有工作树，只建立必要空输出目录；compare 必须等全部五步成功退出。可选 ffmpeg 5f QA 不在此次重放内。
