# S08 F033 call16 来源保全与便携同 raw 重放

唯一最终图 SHA256：0f8637f7f1cf5cc01e99029da5da13c9c42bac06329e2b64d77980d997029b47。

## 实际生图证据

- 实际请求：F033_native_call16/request.json，SHA256 4bafeebee2656597e0539db325d1ea93887b2396c5b4f39357c92937ceb001cf。
- 实际 prompt 与五张有序参考均原字节保留。首参考必须是 F033_actual_edit_target_AA54_1p5x_RGBA.png。
- call16 raw：F033_native_call16/raw/F033_whole_turn_arms_native_raw.png，SHA256 8828aafd54c8e53430be57b425ea5c4c6a651c9519cdc1c1ae31f2d362908401。
- 本状态实际 1 call / 1 raw；截至该调用共 16 次有效调用、16 张 raw、17 次工具提交，含此前 1 次参数验证失败。v1–v5 都是同一 raw 的后处理版本，不计生图。
- pre_AA54 是未采用的早期 54px 透明孔输入门历史，与真正提交的五参考严格分开；它不增加本次工具调用计数。
- MINIMUM_SOURCE_RECEIPT.json 是先交最小九项时的时间点快照；最终封存状态另见 F033_FINAL_LOCKED/HAND_REUSE_CONTRACT.json 与 SEALED_MANIFEST.json。

## 便携重放

运行：python run_isolated_replay.py --sandbox /tmp/f033_replay_new --verify-against final/S08_F033_whole_turn_same_raw_final_color_RGBA.png

sandbox 必须不存在。runner 只复制六张 PNG、脚本和依赖清单。无需外网、无模型调用、无安装、无生产写入。

六张计算输入：上一张真实锁定 F030 的 RGBA、F030 near / distal / far / box 四个显式 mask、call16 原始 raw。脚本重建 F030 body 分层，重建 F033 原像素预放置与全部 AA54 权限 mask，再执行精确 uniform registration、nominal 合成、采用的 semantic v5 和四组软材质色修。

随后重建 F033 独立前景近手、完整底层远手、玉镯 AA 合同 mask、桌上火柴盒，以及三层互斥 RGBA 分层。近手不得从最终叠掌区域裁出；远手不得从033遮挡成图反提。

成品与中间候选均不作为重放输入。成品只在计算子进程退出后由 runner 读出比对。计算进程附带文件读写审计：仅允许声明输入、Python运行时和新输出目录；网络和子进程调用被拒绝。

本包 ISOLATED_REPLAY_LOG.json / REPLAY_RESULT.json 记录通过：最终 PNG 字节一致，RGBA 差异像素 0，最大通道差 0，全部阶段与显式 mask SHA 一致。负向测试覆盖未声明成品读取、raw字节篡改、缺失原件与已有输出目录覆盖拒绝。

## 文件与上传

- ROWS_MINIMUM_ONLY.json：先交九项，保持原内容不变。
- ROWS_SUPPLEMENT_ONLY.json：完整包中除九项外的补充项。
- ROWS.json：全体交付项，含 local_path、path、sha256、git_blob_sha、bytes、upload 与可验证的已知 blob 来源。
- EXISTING_BLOB_REUSE.json：依据本地已有 fixed commit 记录复用 F030 等既有 blob；此工作未发起任何远端读写。
- 原脚本完整保留以审计；replay_f033.py 是只保留确定性计算的便携版，去除预览和原绝对路径，数值、舍入、mask、source-over次序保持一致。
- v1–v4 的小脚本和诊断保留为历史，不重复携带坏候选图或全部工程。

这份复现只证明像素与来源链，不替代独立视觉审查，也不表示真实 Canvas 灯、桌、火、杆场景门已通过。最终独立静态/材质与030×3→033×3隔离状态见原封存合同；真实 Canvas 集成属于另外的审查。
