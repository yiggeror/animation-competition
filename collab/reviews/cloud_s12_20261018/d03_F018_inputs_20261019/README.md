# S12 F018 唯一输入门 · 未执行

按[Astra本次指示](provenance/coordinator_instruction.txt)准备018一态，曝光018–021（4f）。新锁012是连续母；锁000只提供局部材色；原018体量图不变。此包尚无018成图、Canvas或MP4。

| 实际输入顺序 | 文件 | SHA256 |
|---|---|---|
| 1 · 新锁012连续母 | [01_locked_F012.png](inputs/01_locked_F012.png) | `063bc020f65f3e9485a57984f20703f0fbc96667a2f5a046ad713ee51d1beb88` |
| 2 · 锁000纯材色局部板 | [02_locked_F000_materials_ONLY.png](inputs/02_locked_F000_materials_ONLY.png) | `a6a40d2e847b9a9256f20edb46cf8467fe7487deb0dc97448674ec7c7b5e22cd` |
| 3 · 原018体量图，逐字节未变 | [03_F018_CONSTRUCTION_UNCHANGED.png](inputs/03_F018_CONSTRUCTION_UNCHANGED.png) | `bcfaffbed6cca5012be23222cefa1035360cf7c8ede97648de82efc603449b8a` |

[完整prompt](prompts/F018_full.txt)，SHA256 `fbadda161afa5914204269f5383d25dca0ec3a00fc1a733eb4a78767abd89185`；[唯一request](requests/F018_NOT_EXECUTED.json)内含实际三图绝对路径、顺序、SHA及原文prompt，`execution_enabled:false`。路径记录本云工作区；协调检出后需按自己的仓库根映射，输入字节与顺序不得变。

整远左上臂、袖、肘、前臂、腕及开放手继续向前下接近；018双手仍空、远指在实际7px签轮廓上方至少3 scene px，022才拇指首触。近右空手、头颈躯干、下摆布尖及受影花瓣、裤腿双鞋继承新锁012；鹤仍由布承托，签/鹤/布/箱不动。构造图灰旧姿态不作为母稿；藏在衣下的肩体量不可画成胸前球。

材色板取自锁000 `95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793` 的12个局部。每块最多40×40，原始RGB最近邻放大，无调色/铺底合成；没有完整旧姿态，也未把旧103或造型03作为生图输入。[来源裁片及坐标](provenance/material_board_sources.json)可复核，受影花纹单列保留。Image1和3均直接复制原PNG，无重存。

三张实际图已分别用view_image实看，[记录](qa/actual_image_review.json)与[输入验证](qa/input_gate_verification.json)齐。`python tools/verify_F018_inputs.py`核对三源Git字节、三图SHA、12块实际RGB、018原构造状态、prompt/request一致和独占改动域。构造坐标仅是参考；未来成图还须实查整臂、接触与色门，不能把此输入验证当作实际018通过。

本轮生图0、在飞0、实景渲染0、新人物成图0；S12历史累计仍4次。仅有018一个禁用请求，022/026/030未开。私有分支`cloud/s12-reference-20261018`交Astra审输入；未动共享实现、留言、ready、EDL或声音，未推共享主分支。
