# S08 首23帧：沿局部灯修新增020×3

入口 `s08_first23_scene.js`，1920×1080、24fps、23/24秒。000–019逐帧保持局部灯修候选的图层绘制、光火与曝光；020曝20–22，023及以后全部入口抛错。局部灯从000保持高初位角−.85，罩未升、芯未点。未引入023以后姿态。

依赖：旧首20源 `6f73473a8230ed7a1b236f32605e622769d29109`；F020层源 `1d3f60e361f273c947726a9ea68c24c9344c7422` 的 `collab/reviews/20261018_1824_s08_f020/layers/`；局部灯修 `collab/reviews/20261018_1822_s08_lamp_mechanical_candidate/lamp_mechanical_candidate.js`（SHA256 `171aaace1079af7215788f38ebc2f35e4c0af09d8fd5d722009094443ff90bf1`）。不修改任何已有包或共享helper。

020原母锁定 `ff4fad4d91762f7a5e8687741d0d09747e466474b91c4f4d0d8f9df032d516e6`。三层RGBA互斥精确重建；桌盒1665可见像素只画一次，alpha与可见RGBA和017完全一致。层序仍灯/凳/body/桌前沿/table_box+contact/arms，原桌和contact参数不动，人物x0/y0/sc1。

020原图近手柴已(-12,+5)：语义硬保护7631像素逐RGBA与017相同，源码没有移动人物；火头锚 `(1062,787)`、握点 `(1034,824)`，原光火公式只跟着此真实锚变化。空掌尚未接杆，lift=0。

语法、23f合同/mock、18层SHA、F020像素重合已通过；首20各80时点合同值及20帧绘制参数相同。真实Canvas新增0帧；不得把这些检查当成实际视觉通过。

完整真实23f命令（现有可用云渲环境）：

```sh
node tools/js/frames.cjs collab/reviews/20261018_1828_s08_first23_scene/s08_first23_scene.js build/S08_first23 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first23_1920x1080_24fps.mp4
```

只先核新增F020：

```sh
node tools/js/snap.cjs collab/reviews/20261018_1828_s08_first23_scene/s08_first23_scene.js build/S08_F020_1920x1080.png 1920 1080 0.8333333333333334
```

实渲看019→020：盒保持桌承重，空掌离盒向新高杆；火随真实柴头移(-12,+5)但相位不断；仍未触杆升罩或点芯。首20无损帧应与局部灯修20f一致；023帧不存在。

运行新增仅3个JS。UPLOAD_ROWS.json的18张图均列已有Gitblob复用，不需上传PNG字节；无整母/大图/影片重复。`npm test`；原像素核 `python verify_pixels.py /path/to/astra_s08_first_mother_20261018_1433`。
