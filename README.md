# 奶奶的皮影｜工程源代码

本目录为影片制作工程的源程序与配置文件整理版。文件路径沿用原项目，以保持镜头模块之间的导入关系。

## 代码结构

- `js/film/edl.js`：最终镜头顺序、时长及视频镜头接入。
- `js/anim/`、`js/chars/`、`js/rig/`：人物动作、姿态序列与变形逻辑。
- `js/paint/`、`js/lamp/`、`js/puppet.js`：手绘场景、二维光照、皮影与投影计算。
- `js/code/`、`js/film/`：画面模块、片头片尾与剪辑时间线。
- `task/`、`collab/reviews/`：S12、S14、S31 等镜头仍在使用的独立程序模块及数据映射文件。仅收录运行依赖，不包含评审材料。
- `assets/`：帧曝光、骨骼及动作序列 JSON 配置，未收录图片等媒体文件。
- `src/laidian/`：Python 画面绘制与渲染辅助程序。
- `tools/`：浏览器逐帧导出、视频拼接及工程处理脚本。
- `dev/view.html`：镜头预览页。

## 主要处理流程

最终镜头表由 `js/film/edl.js` 定义；`tools/js/frames.cjs` 通过浏览器逐帧调用各镜头的 `renderFrame()`；`tools/render_film.mjs` 生成分镜片段，`tools/master_film.mjs` 负责按时间线合成为影片。

在具有完整素材的原工程中，可安装 `package.json` 声明的 Node.js 依赖，并准备 FFmpeg 与 Playwright 浏览器环境；随后运行对应渲染和合成脚本。

## 本代码包的边界

本包仅包含源代码、HTML 预览页与 JSON 配置。图像、视频、音频、字体、制作记录、测试报告和生成提示词均未收录。

部分镜头依赖外部绘制的角色逐帧图，因而仅凭本包不能完整复现最终成片。最终剪辑表中 S28、S29 直接接入已完成的视频片段；原项目的对应视频资源也未包含在本包内。文件中的媒体资源路径保持原状，便于与完整工程对应。

原始工程：`yiggeror/animation-competition`
源代码版本：`claude/intelligent-euler-t2so6e` / `1048b28168f6d3d8cdfffb682e8abdacc4ffc5be`
