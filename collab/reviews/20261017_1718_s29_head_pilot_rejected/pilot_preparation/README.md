# S29 单次试点准备与实际结果

结果：见 `RESULT_REJECTED.md`。唯一一次调用已完成，原图因非目标身体漂移及头部接近B而拒用，没有第二次调用。

## 文件

- `request.json` / `prompt.txt`：实际内置imagegen参数与提示；不是待执行批处理脚本。
- `preflight_manifest.json`：实际输入、请求与调用前测量代码/配置的hash。
- `measurement_config.json`：冻结模板框、±24px搜索、A/B两点和独立H、阈值、人工检查项。
- `measure_pilot.py`：只读检查，写JSON；不执行生成，不输出变形图，不改生产文件。两点求全局相似变换；H不进入求解。
- `test_measure_pilot.py` / `test_red.log` / `test_green_frozen.log`：10项测试及先红后绿记录。
- `master_baseline.json`：调用前原图自测，H约0.0046px。后续config仅将状态从draft标为Opus冻结并加入F198/F201元数据，几何模板/窗口/阈值未变。
- `candidate_measurement.json`：唯一输出的原始测量。B/H撞边使匹配失效，7.30px只是形式结果，不是精确真实位移。
- `output/`：字节相同的唯一工具原件副本；原工具文件仍保留。
- `diagnostics/`：真实alpha可见参考、原像素结构对照；不作为生成输入或生产资产。

## 重现检查

仅在本工作目录运行：

    python -m unittest discover -s pilot_preparation -p 'test_*.py' -v
    python pilot_preparation/measure_pilot.py pilot_preparation/output/x29_midhead_one_call_original.png --out pilot_preparation/candidate_measurement_recheck.json

第二条应exit 2（拒用/待人工，不是工具故障）。报告路径必须在pilot_preparation内且不能覆盖已存在文件。只接受1024×1536，不自动resize，不全局搜索。工具本身不具备接受/重抽能力；数字通过仍必须逐项看头中间态、身份、手/单签、撑地和颈领。

本目录不是仓库代码，未运行成片项目测试/渲染；只验证该独立测量工具的全部10项测试。没有下载历史视频或整仓副本。

## 包目录与元数据修正

保持工作根下 `pilot_preparation/` 与 `refs/` 为同级目录，冻结脚本可原样运行。父线程会复用已提交的参考blob；本包只带参考身份/hash，不再次复制这两张图。检查脚本的A输入为 `refs/x29_look_a.png`，生成参考B为 `refs/x29_head_b_visible_alpha_composite.png`。

最初元数据经过shell双重转义写成字面\n，非有效JSON；修正时原文件已被替换。`tool_result_metadata.raw.txt` 使用当时相同序列化/写入命令忠实复现该错误字节序列，明确不是另一份工具返回。有效 `tool_result_metadata.json` 直接保留同一返回的output_hint文字；像素payload保存在原始PNG，未修改工具输出。
