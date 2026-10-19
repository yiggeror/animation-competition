# S08 三链独立重放结果

PASS。已关闭原来源包中“未执行端到端 replay”的缺口。原已提交来源包未被修改。

从封存 call18/19/20 raw、实际冻结输入和必要保护 mask 起步，先重放 F038，再用重放出的 F038 接 F041，再用重放出的 F041 接 F043。没有预放这三态的任何 final、分层或中间候选；仅 F036 两个前序依赖和原 122 像素释放 mask 作为已知输入。

- 11 个采用脚本全部成功，3 母图与 9 张三层 PNG 的 SHA256 精确匹配原来源包记录。
- 三份原始 RGBA 三层重建逐像素一致。
- 247 个生成产物逐一比对：236 个逐字节相同；8 个 JSON 只有独立副本根路径变化；3 份封存清单另包含这些路径变化文件的 SHA256 和字节数变化。没有实质图像、参数或处理差异。
- 仅两份 semantic build.py 副本替换一个绝对 R 根路径；其余 9 个执行脚本未改。
- 使用冻结配准数值，未重跑优化器、未调用生图、未联网或读写仓库。执行防护拒绝读取作者树及沙盒外写入；无触发阻断。所有原件在重放后重新 hash，未变化。

关键文件：
- reports/REPLAY_SUMMARY.json：短结果。
- reports/REPLAY_FULL_COMPARISON.json：247 项完整 hash、逐层校验、实际读写路径及原文件完整性。
- reports/DIFFERENCES_ONLY.json：仅 11 项真实字节差异及严格分类。
- reports/SEED_MANIFEST.json：种子输入、原 hash、唯一两处脚本根路径替换及运行版本。
- reports/GAP_CLOSURE.json：后续缺口关闭记录。
- reports/*_IO_AUDIT.json、logs/*：每一步的访问审计、耗时、原始 stdout/stderr。
- RUN_COMMANDS.txt、prepare_isolated_replay.py、run_one_guarded.py、run_frame.py、compare_replay.py：实际采用的物化、执行和核对辅助文件。
- worktree/：独立处理副本与真实重放产物。

复跑必须先准备新的空目录，并修改物化辅助脚本的 B 输出根。不得把 B 指向作者根目录，也不得将已采用 final 回填为中间输入。原脚本只需要将两份 semantic build.py 的绝对 R 改为新的副本根，其余执行代码保持不变。依赖版本与原包一致：Python 3.12.14、Pillow 12.3.0、NumPy 2.3.5、SciPy 1.17.0。
