# S30一次六图短上下文诊断：三组RGBA全部零差

固定执行脚本提交`ca2deeea5b398d07ae44a8cc1f7944fce179c074`，SHA256 `30214ff90cb5fdb412157a0c26f643fbcc382d72083b953c08a1181e98afdf54`。在S29新060六帧完成后，只运行一次原命令，未改脚本、31项锁定源或重渲288帧：

```sh
NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node collab/reviews/20261019_2226_s30_complete_scene_gate/diagnose_s30_finite_contexts.cjs
```

结果`COMPLETED_FINITE_DIAGNOSTIC`、退出码0。fresh页1按`[000,000]`，fresh页2按`[000,190,000,190]`实际绘制，共6次，保存6张原PNG、对应6张原JPEG与3张差图。浏览器/请求/必需HTTP错误均0，31项源渲染前后62条SHA全部通过。

| 实际对照 | RGBA差像素 | 差通道 | RGB最大差 | alpha最大差 |
|---|---:|---:|---:|---:|
| 页1 000第一次→000第二次 | 0 | 0 | 0 | 0 |
| 页2 000第一次→190后000 | 0 | 0 | 0 | 0 |
| 页2 190第一次→000后190 | 0 | 0 | 0 | 0 |

独立Pillow解码六PNG所得完整RGBA SHA与原Canvas读回一致；三组全部像素直接比较为0，三张`ABS_RGB_X24.png`也均为黑RGB/alpha255。12组绘制前后ctx状态完全一致：alpha1、source-over、filter none、单位变换、sRGB/unorm8、willReadFrequently false，完整状态保存在原报告及独立核验中。

本次四张000的JPEG SHA均为历史首张`4a12d38f…68ce27`，未匹配历史失败重复000的`8cd5a3ea…53341`；两张190也匹配既有190哈希。本次短序列没有复现该历史失败。历史失败图本身未保存，不能重建其像素或宣称长上下文不确定性已根治；PNG/JPEG与RGBA读回也可能影响Canvas后端，保留原脚本的限制说明。完整12秒视觉通过采用Astra已给出的终审结果，不用此六图扩大结论。

`actual_six_draws/FINITE_CONTEXT_DIAGNOSTIC.json`为原执行报告，保留所有原PNG/JPEG、区域统计、ctx与源SHA；`CLOUD_FINITE_SIX_INDEPENDENT_VERIFICATION.json`是独立解码/比较证据；`CLOUD_UNIQUE_FINITE_AUTHORITY.json`与stdout记录唯一启动。主审实际打开六图联系表、完整000与190 PNG及差图，实际图像完整；`ACTUAL_SIX_DRAWS_CONTACT.jpg`供定位。

本包只交Astra，不改共享生产、EDL、声音或ready；零新增生图。`verify_saved_finite_diagnostic.py`只核已有文件，不运行浏览器。
