# CREDITS · 素材来源与授权

## 字体
| 字体 | 作者 | 授权 | 来源 | 用途 |
|---|---|---|---|---|
| Noto Sans SC（思源黑体） | Adobe / Google | SIL Open Font License 1.1（`assets/fonts/OFL-NotoSansSC.txt`） | https://github.com/google/fonts/tree/main/ofl/notosanssc | 文档插图、字幕 |
| Ma Shan Zheng（马善政毛笔楷书） | 马善政 | SIL Open Font License 1.1（`assets/fonts/OFL-MaShanZheng.txt`） | https://github.com/google/fonts/tree/main/ofl/mashanzheng | 片名备选 |

## 画面
- 屋子、光照、皮影（鹤、乌龟）、手影狗、影子、手机屏幕：本仓库的程序逐帧计算生成，不使用现成图片素材。
- 人物图（小满、奶奶）、手部特写图（横握手机、捏插头、四只手、狗手影）和屋子底图（`bg_01_room_wide`）：AI 生成。小满坐姿图由用户用生图模型生成；其余由合作 AI（Astra 团队）用内置生图工具生成。每张图的文件、工具、提示词和审查记录见 `collab/refs/`、`collab/partner.md`、`collab/reviews/`，汇总见 `docs/ai-usage-log.md`。程序对这些图做了抠图、法线和材质计算、分层动画和打光（`tools/cutout.py`、`tools/card_maps.py`、`tools/card_soft.py`、`tools/key_thumb.py`、`js/lamp/`、`js/paint/`、`js/code/phone_img.js`）；马灯、樟木箱、插座、手电、火柴、皮影、游戏画面等道具和所有光照由程序画。

## 声音
配乐和音效全部由本仓库的程序合成（`audio/`）：乐器（板胡、笛子、扬琴、琵琶、梆子、板鼓、锣、钹、8-bit 音色）用加法合成、Karplus-Strong 拨弦和模态合成算出来，音效用噪声、振荡器、共鸣滤波和摩擦模型算出来。不使用任何采样、录音或第三方音频素材。主题旋律和各段编排为本片原创。

## 参考资料（不进片）
皮影查证资料见 `docs/research/shadow-puppetry.md` 第 4 节。
