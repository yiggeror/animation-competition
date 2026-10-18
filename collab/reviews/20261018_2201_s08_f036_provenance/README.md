# S08 F036 call17 来源保全与隔离同 raw 重放

最终母图 SHA256：6ee3d4ccf88650496ce97f8709642fb3b5a228fd0ec1a5e5fd4efc50fac42753。

## 实际提交，不混入历史

- F036_native_call17/request.json 是原请求，SHA256 029ba7688874d2ccc40c4503158f038f95aa93dc52d1eeaeaaa063e781a4a728。prompt 原字节保留。
- request 中有序五参考是实际 AIR871_CLEAN target、配套白 mask、033 身份 + 实际 030 灯空间双联图、036 躯干四肢结构图、F000 无手材质参考。每张按原路径原字节封存。
- 五张实际输入均在本次保全时打开核对；此来源辨识不冒充生图前验收或新视觉审查。
- 原 raw：F036_native_call17/raw/F036_whole_turn_arms_native_raw.png，SHA256 0c5406e79310fcbf80739e32de630bfb65d2f9e4f0110b31e4658c7d5d6a951d，1293 × 1217，1,204,441 bytes，与原生成输出逐字节相同。
- 本状态 1 次有效生成 / 1 张 raw。累计 17 次有效调用、17 张 raw、18 次工具提交，其中此前 1 次参数验证失败。v1–v9 与色修都是同 raw 后处理，不是新调用。
- F036_input_gate/history/pre_871_air_islands 是未采用的早期输入门，明确隔离，不作为实际 call17 五参考。
- MINIMUM_SOURCE_RECEIPT.json 与 ROWS_MINIMUM_ONLY.json 是先交的九项来源薄包时间点快照；不因后续层归属调整重写。

## 便携重放

运行：python run_isolated_replay.py --sandbox /tmp/f036_replay_new --verify-against final/S08_F036_whole_turn_same_raw_final_color_RGBA.png

sandbox 必须不存在。无需外网、模型调用或安装。计算子进程仅获 14 项声明输入、10 份原作者脚本、重放器与依赖清单。所有输入先 SHA256 验证。

14 项输入包含：call17 原 raw；上一张锁定 F033 的母图、独立近手、完整底层远手、远近手和盒的显式 guard/footprint；F000 原母图；实际 Canvas F030 灯空间；结构点 JSON；原字体。上游 F033、F000 和实际 Canvas 的角色各自分明。

依次重建 F033 body partition、F036 预放置和全部权限 mask、实际五参考、统一配准 nominal、独立 v9、色修、修正前 archive/partition、53/483 mask、修正后独立手和三层。v9 独立运行，不依赖 v1–v8 的候选。

原脚本按字节保留，运行时仅将 __file__ 定位到隔离输出树，并将字体绝对路径换成已声明原字体路径。配准使用实际冻结 scale/tx/ty；register_raw.py 优化器原件保留作审计，但不重新优化来改变实际执行参数。数值、舍入、source-over 顺序和画面运算不变。

没有将 F036 成品、nominal/v9 中间图或 53/483 mask 作为计算输入。修正前的历史近手/远手/盒层也由同 raw 当场重建。最终图仅在计算进程退出后由 runner 读出作外部比对。读写审计限制声明输入、系统运行时和新输出目录，并拒绝网络与子进程。

ISOLATED_REPLAY_LOG.json / REPLAY_RESULT.json 已记录实跑通过：73 个输出 SHA 一致，最终 PNG 字节相同，RGBA 差异像素 0、最大通道差 0。负向测试覆盖 raw 缺失、字节篡改、未声明成品读取、网络创建以及已有输出覆盖拒绝。

## 近手、真实远手和层归属

- 近手始终来自独立前景 RGBA，不从已叠远手的最终 AA 边缘反提。distal 原掌、手指、整根火柴不被局部 collar 修补替代。
- 完整真实远手与玉镯独立保留在近前臂下方。2191 个旧外侧透明 footprint 像素被显式释放；真实握口和 lever seat 不等同于泛化外侧空气。
- 150 个真实玉镯部分 alpha 边缘按原前景 source-over 新的真实袖口/皮肤底层。不能把玉镯重新粘到近前臂上方。
- mask 名 SAME_RAW_far_wrist_collar_smooth6right2down.png 是历史名称。v9 实际代码是 X−10×weight、Y 不变，即水平最多右移 10 px、竖向 0；以保留代码为准，不改 PNG 名称冒充别的执行。
- 53 个旧蓝领 archive 像素（10 opaque + 43 AA）仅从独立近手档排除，且不属于 distal guard。此处最终可见像素属于真实远手后层，不应复制进近手。
- 483 个原 F033 母图盒外沿像素回到 body-behind-table；runtime table box 恢复原 033 的 1665 个可见像素。母图 6ee3 不变。两修正 mask 由原作者 rebuild_explicit_masks.py 从当场重建的历史层和最终母图求出。
- 三层保持原 RGB、互斥 alpha，逐 RGBA 精确重建母图。这里验证像素和来源，不代替实际 Canvas 灯、桌、火焰、前侧管经过的视觉审查。

## 上传清单

- ROWS_MINIMUM_ONLY.json：先交九项，内容保持不变。
- ROWS_SUPPLEMENT_ONLY.json：除九项外的补充来源、依赖、脚本、mask、合同和重放证据。
- ROWS.json：完整交付清单，每项含 local/local_path、仓库 path、gitsha/sha、sha256、bytes、upload。
- 薄九项已由协调者在 commit 38b2f9d13bc6ec7bbd190742e5ae245cc99bb33d 固定读回 9/9，不重复上传；原薄包清单保持不变，完整 ROWS 标注 reuse。其余补充项 upload 默认 true，远端安全去重由唯一仓库协调者核实。本任务没有外部写入。
- SOURCE_MANIFEST.json 记录作者原件来源和角色；历史或中间候选主要保留脚本/诊断与 hash 索引，避免混称最终或重复携带大图。

独立视觉状态以协调者及作者审查回执为准。数值相同、重放通过、材质均值或 layer reconstruction 均不单独构成视觉验收。

## 分层增量验收补充

协调者 2026-10-18 22:09:07 UTC 直接报告：已独立实看盒来源四图，原盒 1665 可见 RGBA 同 033、alpha 重叠 0、母图 6ee3 重建 0 差；builder 另核真盒、148 个低杆遮挡像素和近档 distal 0 差，本次增量门已确认。原作者待审回执仍原样保留，更新单独记录于 INCREMENTAL_LAYER_ACCEPTANCE.json。此消息不扩展为对其他场景或新画面验收。
