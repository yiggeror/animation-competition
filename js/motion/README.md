# 3秒代码关节动作验证

这是独立运动小样：小满平足准备、踮脚伸手、连续闭指握绳、下拉、松指撤手、落跟。固定机位、960×540、24fps、72帧，无姿态图切换或淡化。它验证代码驱动关节与接触的可控性，**不是连续生图能力的证明，也不是可直接采用的正式镜头**。

人物使用既有 `js/cut/xiaoman.js` 的程序剪纸造型副本，局部改为白圆点连衣裙、连续指骨及腕部控制。头脸、眼睛、发型和比例与正式小满存在明显差异。身体曲线为协调运动学设计，没有做质量与力学平衡仿真。是否自然、是否适合成片，必须与几何连续性分开判断。

仅新增本目录、`tools/motion/` 和 `dev/motion/`，原有cut文件、镜头、EDL及声音不变。没有新增生图或付费视频生成，没有启动Blender。

## 查看与复现

在仓库运行 `npm run serve` 后打开 `http://127.0.0.1:8080/dev/motion/proof.html`。页面可播放、拖动时间和开关骨架/接点显示。先看普通画面，再用叠加诊断。

```bash
node tools/motion/check_proof.mjs /tmp/motion_constraints.json
node tools/motion/render_proof.cjs /tmp/motion_normal normal
node tools/motion/render_proof.cjs /tmp/motion_skeleton skeleton
ffmpeg -framerate 24 -i /tmp/motion_normal/f%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p /tmp/motion_normal.mp4
```

渲染脚本需要Playwright及`/usr/bin/chromium`；当前云端调用还设置了已安装依赖的`NODE_PATH`。每组渲染生成来源前后哈希、72张原PNG和逐帧关节/接点记录。数学检查覆盖721个时间采样，但其通过不等于表演审美通过。

已冻结的v1保留原腰缝和钩指问题；v2只合并连衣裙轮廓、修改闭指终角和拇指对握，身体、腿、腕及绳的72帧状态不变。交付记录和独立审查在协作分支的`collab/reviews/`，不得将作者自评当作独审结论。
