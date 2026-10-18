# S08 最新用户图：仅双手与道具试接

用户最新原话（根线程转述，原文保留）：
- Sentinel_24d8b938225081919a15e4ab0a9d4252：这张好些吧？
- Sentinel_37779d18fa908191b243efbbc4c5a077：不是只看双手吗，先用上试试吧，opus那边在等
- Sentinel_c99168fcd2ec819190f33e982595708d：注意分工别乱了哈

## 直接取用
- `originals/user_latest_atlas.png`：用户最新原件，1717×916 RGBA，SHA256 8c3eea60890f0dbfb03f0659cea6bcad2758ca4d551936d208ef19b4b31ae90f。不是上一张PNG，也不是截图。
- `candidates/left_hand_box.png`：左手、玉镯与盒，腕部切口不代表已接回。
- `candidates/right_hand_match.png`：右手与整根未点火柴，腕部切口不代表已接回。
- `candidates/hands_and_props_registered.png`：两部件保留原图相对位置，供快速试摆；坐标详见manifest。
- `manifest.json` 的 source_crop_xyxy 是原始1717×916像素坐标，只有裁切，无缩放/旋转/姿势变化。两份 selection 是选择范围，actual_alpha 才是最终透明度。

Astra只在副本做显式alpha裁切及低alpha/彩边清理，所有保留RGB仍是用户原像素；原件完整保全。没有追加生成，没有重画胸袖或改主实现。右腕为开放接入口，左镯旁仅少量原腕肉；不带坏胸袖整体贴回。

## 分工与状态
按用户要求立即交 Opus 试接。Opus负责实际机位、合成、接回或局部取用及渲染；Astra收到实际帧/片再独审。这是手部素材候选，不是整图结构、双腕接回、连续动作或最终成片通过。必要时可直接从附带原件改取范围，不要把切口当成画内自然末端。

当前 af8bfe2 的 S08 实现/冻结参考仍为中景，仅3%推近，旧arm atlas mask覆盖肩/肘/镯腕，镯腕约(859,821)，桌前遮挡y981才开始。所以上一版按旧mask整体贴回会显示近端连接；不能据“只取手”的本次方案断言旧整臂结构已解决，也不以旧整臂问题拖住本次手部试接。

qa/previous_input_* 是上一张用户图的同机位/旧mask诊断，仅解释取用范围，不是新图或最终编码成片；其中合成有诊断拼接边，不作为画面通过证据。
