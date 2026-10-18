# S13 d02–d04 小段 · 沿锁定母态顺链交回 Astra

最新状态：Astra已锁本页三张采用PNG，原SHA不变；当前d05–d07小批见 [新入口](../d05_d07_segment/README.md)。以下保留 `0c0f62d` 当时的交付与自审记录。

**本轮3请求/3原件，d02→d03→d04依赖完成，作者已实看自审，待Astra小段回审。** 全部来自真实图像工具编辑；没有15张独立抽。唯一锁定源为 d01 配准PNG `91715601ae814bd84a3dc8d6ce43f1cc809a7bdd74e7390fefffe579f6882050`。授权原文见 [母态锁定与小段授权](../provenance/astra_d01_lock_and_segment_gate.md)。

## 优先看

- [四态同尺度总览](qa/00_d01_d04_same_scale_actual.jpg)：已锁d01 → d02眼先右上 → d03整头右转 → d04清醒收口。
- [d02→d03 整头同尺度前后](qa/d02_d03_same_scale_whole_head.jpg)：头发外轮廓、耳花、发根、远眼与鼻颌共同变化，完整颈领进入原场景位置，不是只挪五官。
- [d03→d04 同尺度收口前后](qa/d03_d04_same_scale_closed_mouth.jpg)：闭唇无口腔/舌残留；嘴外像素不动，眼睛仍清醒。
- [d01→d02 眼区近图](qa/d01_d02_actual_eyes.jpg)、[三态三底实看](qa/all_three_poses_on_three_backgrounds.jpg)。
- [36f隔离画层曝光](qa/isolated_36f_layer_preview.mp4)、[实际解码边界帧](qa/decoded_36f_exposure_contact.jpg)：1280×720、24fps、36f/1.5秒，0×18、18×6、24×6、30×6。**只有实际PNG与中性底，无音频、无灯光、非Canvas接景渲染，不能当完整S13验收。**

## 唯一取图

1024×1536 RGBA，同画布，直接沿已锁配准源的场景接口 `.85+(330,−30)`；不得再次套d01原件→配准的 `.930232558` 变换，否则重复缩放。

| 起帧 / 停 | 采用文件 | SHA256 |
|---|---|---|
| F018 / 6 | `approved_local/F018_d02_eyes_up.png` | `306ac1e2013a020b6a2e177d150f58ca34d1b17cdbbfc5488f166013dc06cd7e` |
| F024 / 6 | `approved_local/F024_d03_whole_head_right.png` | `c04f4fcc60e6539cd7de3048e692a1986866e24cfffe4c702f03538c19decd5e` |
| F030 / 6 | `approved_local/F030_d04_awake_closed_mouth.png` | `994b085de94c9accbadfd9dea858aaa41814376ce42280b6a3c5fb3846b9f590` |

`approved_local` 是作者自审，三张仍待Astra回审。F000–017继续使用已锁d01原文件，不复制新母态、不沿原始d04整图推进后链。

## 源像素处理与实审

**d02：** 图像工具实际编辑了双眼向右上看，但整图也有无关重绘。因此只接回两眼范围的真实生成RGB，范围外逐RGBA继承d01，整张alpha也继承d01。没有用代码画眼珠或改眼白形。检查实际近图，两眼目标一致，头身/嘴不抢动。`qa/d02_validation.json` 证实范围外0改、alpha0改。

**d03：** 从已自审d02生成完整头部转向。实际可见后脑、刘海、近耳位置/露出、花及发根、远眼短缩、鼻颌和颈面共同变化。保留工具原生的头—颈—白领—上肩单元，领下胸衣继承母态（源y≥1120逐RGBA同）。不声称字面精确7°，请沿同尺度图判断视觉增转和衔接。

最初拼接试图强锁旧领缘和按颜色保护旧衣料，实看出现双线、辫梢裁缺及领缘小三角，全部退回，未作d04输入。最终改为保留完整原生颈领连接，不再强行拼旧边界；这一步没有追加生图，也没有手工补画解剖。**白领/上肩有真实新像素，不能宣称白领0改。** 原始生成完整保留，最终范围见 `masks/d03_whole_head_neck_scope.png`。

**d04：** 从最终已自审d03生成。工具输出闭口正确，但整图意外放大，故拒用整图；只采用实际闭口区域，经 `(-23,+21)` 源像素整数平移接回d03，不缩嘴、不挤脸、不绘制唇线。嘴区外逐RGBA与d03相同，alpha全图相同；无剩余舌/口腔，清醒上视保持。原始整图的尺寸漂移在 `originals/` 保全，不作为生产母态。

接回范围仅选择真实生成像素，羽化只用于区域边界，未做代码人物或手绘五官。所有alpha/颜色策略、确切mask、来源SHA和边界验证都在逐态JSON中。

## 完整请求、来源与复现

- `requests/call_002/003/004_request.json` 保存实际完整工具参数与提示词，`*_response.json` 保存输入/输出SHA与来源路径，`*_tool_return_metadata.json` 保存完整返回提示。图像模型版本未由工具返回，不猜模型名。
- `originals/` 是3个工具原件逐字节副本，默认工具路径也仍在 `/workspace/generated_images/`。全项目累计4次图像请求/4原件，本轮无失败调用。
- 按顺序运行 `python3 .../tools/assemble_segment.py d02`、`d03`、`d04` 可重放采用PNG；再运行 `python3 .../tools/build_qa.py` 重建同尺度图与隔离曝光检查，不调用图像服务。
- `qa/d02_validation.json`、`d03_validation.json`、`d04_validation.json` 只证明采用范围与像素继承；不代替主观表演判断。`qa/exposure_36f_validation.json` 证实编码后F017→018、023→024、029→030确实按表切换。

当前小段已交回，未开d05。后段哈欠、闭嘴再扭开及F100尾落定仍须后续实际绘图与曝光核验；未改公共模块、EDL、音频、留言或ready。
