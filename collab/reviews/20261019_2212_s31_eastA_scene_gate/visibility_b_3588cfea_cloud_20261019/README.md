# S31固定3588cfea：一次五张原PNG诊断，整体HOLD

已按Astra指定顺序，在S29修复/24帧及S30唯一全288帧完成并固定后，沿`3588cfeae7e1de0d816c990032db3801e550347d`执行一次：

```sh
NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node scene_preview/render_visibility_and_b_diagnostic.cjs
```

工作目录是固定源码的隔离副本`/tmp/s31-visibility-b3588cfea-20261019/collab/reviews/20261019_2212_s31_eastA_scene_gate`。38项固定文件逐字节提取并在运行后再次核SHA；输入索引28项全部通过。原脚本无修改，正好5张960×540原PNG，退出码2；没有重复启动、全336帧渲染、新生图或共享生产修改。

## 五张实际原图

`actual_five_pngs/`依次保存：

1. `B180_FRESH_FIRST.png`：fresh上下文原B第一次。
2. `B180_FRESH_REPEAT.png`：同页不经A，再画原B。
3. `A000_VISIBILITY_CANDIDATE.png`：另fresh上下文候选A000。
4. `A116_VISIBILITY_CANDIDATE.png`：同页候选A116。
5. `B180_FIRST_AFTER_A.png`：该页A后第一次原B。

原日志`VISIBILITY_B_DIAGNOSTIC_ACTUAL.json`、stdout、实际启动/完成记录、固定输入索引和独立PNG解码结果均保留。PNG字节SHA及解码RGBA SHA全部与浏览器记录一致，alpha均255。`ACTUAL_FIVE_PNG_CONTACT.jpg`为定位联系表；`A000_A116_ACTUAL_EAST_BACKGROUND_2X.jpg`仅放大既有实图，不能替代原尺寸可读性门。

## 严格RGBA结果

| 对照 | 差通道 | 差像素 | 最大通道差 | 结论 |
|---|---:|---:|---:|---|
| fresh原B→无A自重复B | 6 | 6 | 1 | 非零 |
| fresh原B→A后首次B | 6 | 6 | 1 | 非零 |
| 自重复B→A后首次B | 0 | 0 | 0 | 精确相同 |

前两项是同6个坐标和通道：`(913,486)G−1`、`(29,491)G−1`、`(29,494)B−1`、`(28,521)G−1`、`(914,525)B−1`、`(28,534)G−1`。全部改变像素的前后完整RGBA及四通道delta在`FULL_RGBA_DIFF_1.csv`、`FULL_RGBA_DIFF_2.csv`，无截断；第三个CSV为零差表。

本次控制证实，无A自重复也出现相同残差，而本次自重复B与A后B完全一致；不能单凭fresh差异把这6点归因于A。仍按原fresh基准保留严格隔离HOLD，不以阈值、JPEG或肉眼近似改签零差，也不据一次控制外推所有时刻。

## 实际暖光可辨性：尚未通过

主审与现有只读云审均实际打开五张原PNG和2×定位图。A000/A116右下包及内物已入框，东侧奶奶位置可读；但原尺寸下包仍主要是暗蓝块、内物为暖橙模糊条，半开唇口和原鹤的红头—弯颈轮廓不能可靠辨认。2×图仅能定位，不足以证明原鹤可读。保留原14px统一背景虚焦与实际暖光，不用CPU几何可见替代成片视觉结论。

前景小满尺寸、下巴手电、真实龟及两签未见新增关系问题；三张B肉眼未见可见漂移。此有限观察不覆盖严格RGBA失败，也不代表整镜ready。交Astra审查取舍，不自行改源或补一次渲染。

详见`CLOUD_FIVE_PNG_VERIFICATION.json`与`ACTUAL_PNG_VISUAL_REVIEW.json`。`verify_five_pngs.py`只读取已生成五PNG、独立重算完整RGBA差并核源，不调用浏览器。
