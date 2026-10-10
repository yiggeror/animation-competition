# 《来电》

全国大学生数字媒体科技作品及创意竞赛 · 影视/动画赛道 · 2D 动画短片（无对白，约 4 分 50 秒）。

> 停电了。奶奶从木箱里翻出一套皮影，祖孙俩在床单上演起了《龟与鹤》。最热闹的时候，来电了。

**画面全部由本仓库的程序逐帧计算生成**——不是录屏，不拼现成素材，不用 AI 生成的图片。影子和光由真实的光照计算得出：马灯、手电、日光灯都有真实的位置和大小，皮影的彩色影子是光线穿过雕花牛皮算出来的。

## 目录
| 路径 | 内容 |
|---|---|
| `docs/brief-v2.md` | 团队的制作提示词（原始需求） |
| `docs/research/` | 皮影查证 |
| `docs/preproduction/` | 剧本 v3、节拍表与能量曲线、平面图、镜头表 |
| `docs/design/` | 画风方向、人物 / 皮影 / 场景设计说明 |
| `docs/ai-usage-log.md` | AI 使用记录（哪些是 AI 做的，哪些是团队的决定） |
| `src/laidian/layout.py` | 堂屋布局：全片唯一的空间数据来源 |
| `src/laidian/render/` | 渲染器：光线追踪、光源与阴影、床单透光、皮影、人物、画风合成 |
| `src/laidian/shots/` | 各个镜头 / 样张 / 设计稿的脚本 |
| `tools/` | 平面图、能量曲线、检查用的小工具 |
| `renders/` | 提交到仓库的预览图和小样（完整高清版另存，见下） |
| `PROGRESS.md` | 进度 |
| `CREDITS.md` | 素材来源与授权 |

## 怎么重新生成

### 环境
- Python 3.11+，依赖：`pip install numpy scipy numba pillow`
- ffmpeg（拼视频用）
- 字体已在 `assets/fonts/`（SIL OFL 授权）

### 命令
```bash
export PYTHONPATH=src

# 平面图、剖面图、能量曲线
python tools/draw_floorplan.py
python tools/draw_tension.py

# 第一个检查点的全部图：画风样张（1920×1080）、设计稿、动态小样
bash tools/render_checkpoint1.sh build/checkpoint1

# 单独跑某一部分
python -m laidian.shots.style_samples build/samples --w 1920 --h 1080 --ss 2 --moments 6,10,10w
python -m laidian.shots.design_sheets build/design --only characters,expressions,puppets
python -m laidian.shots.motion_sample build/motion --w 960 --h 540
```
渲染在 CPU 上进行（numba 多线程）。1920×1080 的一帧约 2–4 分钟（4 核）。

## 技术路线（简述）
1. **场景**：堂屋按 `layout.py` 的尺寸搭成三维几何（解析几何体 + BVH），逐像素光线求交。
2. **光**：每个光源有真实的位置和大小（马灯 = 火苗 + 被熏黄的玻璃罩，日光灯 = 线光源，手电 = 带光斑轮廓的聚光，月光 = 有角直径的平行光）。阴影由光线追踪算出，半影宽度由光源大小和距离决定。间接光用虚拟点光源近似。
3. **床单**：两面受光——背后的灯透射过来，前面的灯反射回去；被照亮的床单本身又作为面光源照亮人。来电时影子"消失"是因为日光灯从正面把床单照亮、压低了影子的对比度，不是手动擦掉。
4. **皮影**：每个部件是一片带透射贴图的牛皮，阴影光线穿过它时被染色；离床单越远，影子越大越虚。
5. **人物**：三维骨架 + 有向距离场的连续形体（关节处没有缝），IK 摆放四肢；渲染出几何、法线、光照等缓冲，再由画风合成画成二维。
6. **画风合成**：同一套光照缓冲，三种画法（灯影 / 刻光 / 绢灯）。明暗、阴影都来自光照计算，不是滤镜。
