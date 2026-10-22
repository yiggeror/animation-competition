# CREDITS · 素材来源与授权

片名《奶奶的皮影》。片尾"制作与资源"（`js/code/making.js`）只列技术手段、工具、字体和声音来源，内容与本页一致。人物画稿的流程：角色母版 → 2D 骨架参考图（`tools/keyframe_refs.py`，按母版骨长、两节 IK）约束关键姿势 → 生成式图像模型以母版为底出关键帧 → 抠图分层、定位点注册、逐格曝光表 → 由轮廓推算法线图与材质图进入同一套光照。

## 字体
| 字体 | 作者 | 授权 | 来源 | 用途 |
|---|---|---|---|---|
| Noto Sans SC（思源黑体） | Adobe / Google | SIL Open Font License 1.1（`assets/fonts/OFL-NotoSansSC.txt`） | https://github.com/google/fonts/tree/main/ofl/notosanssc | 文档插图、字幕 |
| Ma Shan Zheng（马善政毛笔楷书） | 马善政 | SIL Open Font License 1.1（`assets/fonts/OFL-MaShanZheng.txt`） | https://github.com/google/fonts/tree/main/ofl/mashanzheng | 片名、片尾片名卡 |

## 画面
- 屋子、光照、皮影（鹤、乌龟）、手影狗、影子、手机屏幕：本仓库的程序逐帧计算生成，不使用现成图片素材。
- 人物图（小满、奶奶）、手部特写图（横握手机、捏插头、四只手、狗手影）和屋子底图（`bg_01_room_wide`）：AI 生成。小满坐姿图由用户用生图模型生成；其余由合作 AI（Astra 团队）用内置生图工具生成。每张图的文件、工具、提示词和审查记录见 `collab/refs/`、`collab/partner.md`、`collab/reviews/`，汇总见 `docs/ai-usage-log.md`。程序对这些图做了抠图、法线和材质计算、分层动画和打光（`tools/cutout.py`、`tools/card_maps.py`、`tools/card_soft.py`、`tools/key_thumb.py`、`js/lamp/`、`js/paint/`、`js/code/phone_img.js`）；马灯、樟木箱、插座、手电、火柴、皮影、游戏画面等道具和所有光照由程序画。

## 声音
- **配乐**：本仓库的程序合成（`audio/inst.py`、`audio/score.py`）：板胡、笛子、扬琴、琵琶、梆子、板鼓、锣、钹、8-bit 音色用加法合成、Karplus-Strong 拨弦和模态合成算出来。主题旋律和各段编排为本片原创。
- **音效**：10-22 起换成真实录音，全部来自 Freesound、授权为 CC0 1.0 公有领域（逐条打开页面核对过，`tools/pick_sfx.py`），文件在 `assets/sfx/`，清单 `assets/sfx/manifest.json`。
  程序负责切分、对位（按画面帧号）、响度对齐、混响与声像（`audio/rec.py`、`audio/build.py`）。手机提示音、游戏 8-bit 小曲、显像管的嗡声和消磁声、马灯火苗仍由程序合成。
- 人物没有台词，也不放语气声（10-22 试过一版，用户听后决定先去掉）。

| 用在 | 录音 | 作者 | 授权 |
|---|---|---|---|
| S08 划火柴 | [Match - Strike and Light 02.wav](https://freesound.org/people/JarredGibb/sounds/248236/) | JarredGibb | CC0 1.0 |
| S08 灯罩落座 | [small wine glass.wav](https://freesound.org/people/Tairblenn/sounds/549899/) | Tairblenn | CC0 1.0 |
| 各种拨杆、开关、提梁 | [Switch Flip #1](https://freesound.org/people/IanStarGem/sounds/278205/) | IanStarGem | CC0 1.0 |
| S07 搪瓷盆放地上 | [Hitting a metal basin.wav](https://freesound.org/people/Sadiquecat/sounds/659438/) | Sadiquecat | CC0 1.0 |
| S07 手机落席 | [phone cordless plastic put down on table.flac](https://freesound.org/people/kyles/sounds/637747/) | kyles | CC0 1.0 |
| S07 仰面躺倒 | [BodyFall.wav](https://freesound.org/people/000600/sounds/187136/) | 000600 | CC0 1.0 |
| 火柴盒、手电落箱、乌龟翻倒 | [Thud / Falling on wooden floor / Snapping, breaking neck](https://freesound.org/people/Breviceps/sounds/447922/) | Breviceps | CC0 1.0 |
| S07 蹭竹席 | [Blanket Movement 6](https://freesound.org/people/OwlStorm/sounds/320144/) | OwlStorm | CC0 1.0 |
| S14 拖凳子 | [Chair Movement 02.wav](https://freesound.org/people/LilMati/sounds/364988/) | LilMati | CC0 1.0 |
| S07/S14 凳子 | [Chair Movement 01.wav](https://freesound.org/people/LilMati/sounds/364985/) | LilMati | CC0 1.0 |
| S14 床单甩上铁丝 | [Fabric Flap.wav](https://freesound.org/people/akennedybrewer/sounds/389170/) | akennedybrewer | CC0 1.0 |
| S14/S29 布料 | [Clothes Rustling 1](https://freesound.org/people/WasabiWielder/sounds/334219/) | WasabiWielder | CC0 1.0 |
| S12/S29 包布 | [foley cloth rustle.wav](https://freesound.org/people/martian/sounds/19291/) | martian | CC0 1.0 |
| S12/S17/S29 皮影牛皮 | [LeatherRustle.L.wav](https://freesound.org/people/jfreem3/sounds/108533/) | jfreem3 | CC0 1.0 |
| S14 衣夹 | [Clothespin - snap - wood - close.wav](https://freesound.org/people/ValentinPetiteau/sounds/624484/) | ValentinPetiteau | CC0 1.0 |
| S14 铁丝、挂钩 | [MetalDrop.wav](https://freesound.org/people/nickronk123/sounds/489767/) | nickronk123 | CC0 1.0 |
| S09 手电开关 | [Torch Click 2](https://freesound.org/people/BenjaminNelan/sounds/410360/) | BenjaminNelan | CC0 1.0 |
| S09 手电推亮 | [Flashlight Clicking On.wav](https://freesound.org/people/baidonovan/sounds/187335/) | baidonovan | CC0 1.0 |
| S08/S09 轻敲 | [Tap on Shoulder](https://freesound.org/people/njjjjjjjjjjjjjjjjjjjjjjjj/sounds/566685/) | njjjjjjjjjjjjjjjjjjjjjjjj | CC0 1.0 |
| S06 插插头 | [plug getting connected to wall socket](https://freesound.org/people/preyk/sounds/525017/) | preyk | CC0 1.0 |
| S06 拔插头 | [Power Cord Unplug 1_2](https://freesound.org/people/Joao_Janz/sounds/477641/) | Joao_Janz | CC0 1.0 |
| S30 拉灯绳 | [Pull switch.m4a](https://freesound.org/people/Chilsville/sounds/591569/) | Chilsville | CC0 1.0 |
| S04/S30 电视断电 | [tv_switch_off](https://freesound.org/people/vhoyer/sounds/869534/) | vhoyer | CC0 1.0 |
| S27 日光灯启辉 | [Fluorescent lamp start 8.wav](https://freesound.org/people/gilligan_itm/sounds/145120/) | gilligan_itm | CC0 1.0 |
| 日光灯嗡声 | [Fluorescent light buzzing](https://freesound.org/people/Rvgerxini/sounds/474312/) | Rvgerxini | CC0 1.0 |
| 吊扇 | [Ceiling Fan (Indoor).wav](https://freesound.org/people/liferecorded_archive/sounds/345230/) | liferecorded_archive | CC0 1.0 |
| S20 签子相碰 | [Sticks.wav](https://freesound.org/people/abstraktgeneriert/sounds/348959/) | abstraktgeneriert | CC0 1.0 |
| S17 鹤嘴撞龟壳 | [Knocking on Wood Door (1)](https://freesound.org/people/Flem0527/sounds/629987/) | Flem0527 | CC0 1.0 |
| S03b 咬西瓜 | [Bite (Apple)](https://freesound.org/people/wadaltmon/sounds/275015/) | wadaltmon | CC0 1.0 |
| 夏夜蟋蟀 | [Night Crickets Back Porch.aiff](https://freesound.org/people/hdfreema/sounds/333221/) | hdfreema | CC0 1.0 |
| 蛙鸣 | [FrogsAndCrickets_ExcerptB_JMA_24Bit_48k.wav](https://freesound.org/people/greysound/sounds/32655/) | greysound | CC0 1.0 |
| S25/S26 手影小狗叫 | [Puppy Bark](https://freesound.org/people/AntumDeluge/sounds/583142/) | AntumDeluge | CC0 1.0 |

## 参考资料（不进片）
皮影查证资料见 `docs/research/shadow-puppetry.md` 第 4 节。
