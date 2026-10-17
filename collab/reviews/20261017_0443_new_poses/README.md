# S12 与 S09 A 原件交付；手机按压源码补核

2026-10-17 04:43 UTC。两图均由内置 `image_gen.imagegen` 各单次生成，底层生图模型未披露；主审和独立 Astra 已实际查看完整原图与裁片。未缩放、未代码修图、未覆盖旧交付。作者记录按生成时原文保留，其“待独审”状态由本索引及独立报告更新。

| 原件 | 实际尺寸 | 结论 |
|---|---|---|
| [S12 奶奶跪坐持签](../../refs/anim_12_grandma_box_crane.png) | 1536×1024 | 静态有限采用；接木箱、鹤和取出动作待验 |
| [S09 小满持手电 A](../../refs/anim_09_xiaoman_flashlight.png) | 1536×1024 | 持未亮手电的准备态可用；推钮、拍击、点亮待验 |

- [S12 独立报告](s12/independent/report.md)、[作者自检](s12/author/author_self_review.md)、[实际请求](s12/author/request.json)。两签可沿现有可见轴接长；拳后端被遮挡不是重生理由。若换杆向，清原短签后从握点接，避免折杆。近右手裸腕、远左腕绿镯正确。
- [S09 A 独立报告](s09_a/independent/report.md)、[作者自检](s09_a/author/author_self_review.md)、[实际请求](s09_a/author/request.json)。右向三分之四和跪坐可保留；右拇指在开关后缘，只能称准备尝试，不能称已推动。B另做限定右臂抬手编辑，当前本包不包含B。
- [两图交付清单](delivery_manifest.json)含实际尺寸、字节数和SHA-256；原件与生成候选逐字节相同。独审证据均是原像素裁片。
- [手机源码补核](phone_code/report.md)、[96帧采样](phone_code/sampling.json)固定 `fcb7c6d`，主审也执行 `node phone_code/sample.mjs` 复现。新包络在24fps仍有F27–73连续47帧 `press>0.5`，不是重用旧片结论。按压反馈和S04/S05的断电UI时基请修后交实际片；代码测量不等于新手机实片审查。

S20最新 `e90fafb` 已见杆端乘facing与6秒近景切换；手机 `b9e5299` 已局部采用B，当前仍未见对应新视频，不把代码采纳当动态放行。此包只写协作区，不修改Opus实现。
