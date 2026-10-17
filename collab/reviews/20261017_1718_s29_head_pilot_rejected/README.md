# S29 唯一半抬头试点：拒用，未接入

原件及完整证据在 `pilot_preparation/`；简读 `pilot_preparation/RESULT_REJECTED.md`、`pilot_preparation/COORDINATOR_REVIEW.md`。工具仅调用1次，原件 SHA256 `802a4409131c76ec95709e334861c5ae27bf67f35a582fcabf1c708cfd9340d9`。

- 头姿已经接近 B，缺真实半抬头中间角度。
- 静止身体、衣领、膝鞋、撑手和握签均被重绘位移；A/B/H 固定匹配失效，形式 H=7.30px 不是可信精确测值。
- 正确 alpha 复核后背景透明，隐藏 RGB 残底不计新增背景错误。
- 未制生产三图/时表，未进 F198，不自动重抽，不以裁头救活本失败图。

## 路径与复核

`refs/` 为实际两输入及 B 原透明层的相同字节副本，沿用仓库既有 blob，无重复媒体上传。`pilot_preparation/request.json` 和 `preflight_manifest.json` 保留实际调用时本机路径与 hash；这是历史记录，不是可直接重跑的调用。只读测量脚本相对读取本包 `refs/x29_look_a.png`，在本包根目录按其 README 命令运行即可；拒用 exit2 是预期结论。不会触发生成。

此目录只有 collab 候选/审查，生产实现不变。下一步需依据失败原因共同冻结局部头层与真实中间角度，而非重复原提示；奶奶单向收布是独立动作缺口，仍在只读规划。
