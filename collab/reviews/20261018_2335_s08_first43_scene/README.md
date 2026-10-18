# S08 首43候选

入口s08_first43_scene.js，1920×1080、24fps、43/24秒。基于固定first41源29a4bca29ee90eaec1e65c2d61db59047ed8efae，仅新增041×2（41–42），043+所有入口拒绝，未提前点芯。

041母5c20ca471bde6bf832d5fbdee1f018b1119d1890ed34c07feb8d091e906c89be及作者新三层全SHA已核。原RGBA重建全等、alpha互斥；单盒1665可见RGBA/alpha域与038全等，底970，原contact不动；双肘981下0，148px低杆盘与038逐RGBA相同。

真火根/药头接芯(1415,794.572972972973)，木出口(1375.442494558651,818.8258854425643)；contract新增wickTouch:true，旧touching字段仍指擦面接触。041仍wick0，043以后未提供。罩升83.243243、低杆lift1/角−.35保持。近手整条前臂在完整远手前，不在运行里重画复用手档。

旧41合同164子帧、41帧绘制/光火、39旧层字节及原封包全部SHA回归。所有场景函数自async function bg()起逐字节同；人物x0/y0/sc1，灯/桌/光参数不动。新041真实接芯、火焰落根及独立芯未燃的读法、侧管前后与远握位须实际Canvas核；本包新实渲0帧。

## 最短新2帧实际渲染

```sh
node tools/js/frames.cjs collab/reviews/20261018_2335_s08_first43_scene/s08_first43_scene.js build/S08_first43_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.7083333333333333 --to 1.7916666666666667
```

只输出00041.png–00042.png。全片如需：

```sh
node tools/js/frames.cjs collab/reviews/20261018_2335_s08_first43_scene/s08_first43_scene.js build/S08_first43 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first43_1920x1080_24fps.mp4
```

RUNTIME_ROWS共45项：3新JS＋3张041层PNG＋39旧blob。041层可复用作者同批上传的相同blob；最小运行不依赖母图/手档来源长包。SOURCE_RECEIPT保存已读正式源合同SHA，远手159完整AA与本帧可见档分开保全。

npm test为静态与绘制命令回归，不能代替实际Canvas。
