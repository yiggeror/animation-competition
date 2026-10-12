# 《来电》

全国大学生数字媒体科技作品及创意竞赛 · 影视/动画赛道 · 2D 动画短片（无对白，约 4 分 50 秒）。

> 停电了。奶奶从木箱里翻出一套皮影，祖孙俩在床单上演起了《龟与鹤》。最热闹的时候，来电了。

**画面全部由本仓库的程序逐帧绘制生成**——不是录屏，不拼现成素材，不用 AI 生成的图片。床单上的影子按真实几何计算：马灯有真实的位置和大小，皮影离床单越远影子越大越虚，彩色牛皮透出彩色的光。

## 目录
| 路径 | 内容 |
|---|---|
| `docs/brief-v2.md` | 团队的制作提示词（原始需求） |
| `docs/research/` | 皮影查证 |
| `docs/preproduction/` | 剧本 v3、节拍表与能量曲线、平面图、镜头表 |
| `docs/design/` | 画风方向、人物 / 皮影 / 场景设计说明 |
| `docs/ai-usage-log.md` | AI 使用记录（哪些是 AI 做的，哪些是团队的决定） |
| `src/laidian/layout.py` | 堂屋布局：全片唯一的空间数据来源 |
| `js/lamp/` | 第四版：光照引擎、人物卡片、皮影与布景、关键镜头 |
| `js/` | 第二、三版（2D、剪纸片）：绘制库、人物、皮影与影子、镜头、设计稿 |
| `src/laidian/render/` | 第一版（3D）渲染器，保留作过程记录 |
| `src/laidian/shots/` | 各个镜头 / 样张 / 设计稿的脚本 |
| `tools/` | 平面图、能量曲线、检查用的小工具 |
| `renders/` | 提交到仓库的预览图和小样（完整高清版另存，见下） |
| `PROGRESS.md` | 进度 |
| `CREDITS.md` | 素材来源与授权 |

## 当前技术路线（第四版："一盏灯照亮的世界"）
屋子、床单、马灯、月光按真实尺寸建模，在 WebGL 着色器里逐像素计算光照（无头 Chromium 自带的 SwiftShader 软件渲染，结果和显卡无关）；
人物是 2D 设计的"卡片"，由轮廓算法线后参与同一套光照；皮影是刻花、染色的牛皮透光图，床单上的影子由 `js/shadowplay.js` 按几何投影。
- `js/lamp/gl.js`、`js/lamp/shaders.js`：渲染遍（表面 → 空气散射 → 合成 → 泛光 → 调色）
- `js/lamp/cards.js`：由轮廓算法线（精确欧氏距离变换）；`js/lamp/xiaoman.js`：小满
- `js/lamp/crane.js`：鹤皮影；`js/lamp/scenery.js`：皮影布景（荷塘、松枝）
- `js/lamp/s06_key.js`：第 6 场关键镜头（场景尺寸、镜头、动作）；`xm_sheet.js`、`crane_sheet.js`：造型检查图

```bash
npm install
node tools/js/snap.cjs js/lamp/s06_key.js key.png 1920 1080 3.0            # 静帧（参数 = 时间，秒）
node tools/js/frames.cjs js/lamp/s06_key.js build/key --fps 24 --workers 3 --mp4 key.mp4   # 5 秒动态
```

## 第二版技术路线（2D，已被取代）
画面由 `js/` 里的 JavaScript 在 Canvas 上逐帧绘制，用无头 Chromium（Playwright）逐帧导出、ffmpeg 合成。每一帧是时间的纯函数。
- `js/lib/`：手绘笔触、一笔画成的人物（连续外轮廓）、亮边、光照图
- `js/chars/`：小满、奶奶（正面/侧面/背面）、五官、手
- `js/puppet.js`、`js/shadowplay.js`：皮影部件与正向运动学；床单上影子的几何计算（放大、两种半影、彩色透光、签子）
- `js/shots/`：镜头；`js/sheets/`：设计稿

```bash
npm install                       # Playwright（用本机已装的 Chromium）
bash tools/render_cp1_2d.sh build/cp1_2d          # 人物设计稿 + 两段动作测试
node tools/js/snap.cjs js/sheets/characters.js out.png 1920 1080 expr   # 单张
node tools/js/frames.cjs js/shots/s06_test.js build/s06 --mp4 build/s06.mp4  # 一段动画
PYTHONPATH=src python tools/export_puppets.py assets/puppets             # 重新导出皮影贴图
```

第一版的 Python 3D 渲染器（`src/laidian/render/`）保留作过程记录；它算出的布景结论（马灯高度、艺人站位、皮影要靠近灯影子才大而虚）在第二版里继续沿用。

## 第一版怎么重新生成

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
