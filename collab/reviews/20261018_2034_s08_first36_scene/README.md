# S08 首36候选

入口 s08_first36_scene.js；1920×1080、24fps、36/24秒。以固定first33源76ff15e0800e51504bcfe10fec6739556057ea07为基，只增唯一033×3（33–35），036+所有入口拒绝。旧首33真实片已双审通过（实际源c10fa383，MP4 SHA256 13b41cc3b2f3170510d1b7f0b35cde36fcbe86b98214b2717cd55a9f7074938f）；此包没有产生任何新实际Canvas，033新门待实渲。

033唯一SHA 0f8637f7f1cf5cc01e99029da5da13c9c42bac06329e2b64d77980d997029b47。采用作者新033三层，母RGBA逐像素重建全等、alpha互斥，盒1665只一次、双肘981以下0像素。角色x0/y0/sc1，原scene/光火绘制函数全部逐字节同；旧33合同132子帧、33帧绘制/光火、30旧图层字节及原封包SHA全部回归相同。

独立近手在完整底层远手前：1725可见重合像素source-over全等锁母，近手不透明像素全等。低杆148像素盘与030逐RGBA不变：45全透明、94半透明、9原手指遮挡；body/box不挡杆座，人物图内无杆。030与033独立手档并非直接把最终合成像素当作可复用单手。

档案复用注意：远hard guard中(1127,800)有一个RGBA[18,30,18,84]旧孤点，而锁033/近手已透明。作者确认仅冻结复用档遗漏，033母及运行三层不受影响；未来036输入单列排除，不能复活。验证报告保留该1像素差异，不冒称远档全等；本包不覆写原图/档案。

033低杆lift1/角−.35、总升罩83.243243保持，灯芯0。真实火头(1230,707)、木口(1194.9191346191965,737.3699338842536)，火光沿原公式跟随。层序仍lamp/凳/body/桌前沿/table_box+原contact/arms，桌/盒影不动。036及以后未采用。

## 最短新3帧实际渲染

```sh
node tools/js/frames.cjs collab/reviews/20261018_2034_s08_first36_scene/s08_first36_scene.js build/S08_first36_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.375 --to 1.5
```

全片（如需）：

```sh
node tools/js/frames.cjs collab/reviews/20261018_2034_s08_first36_scene/s08_first36_scene.js build/S08_first36 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first36_1920x1080_24fps.mp4
```

实渲门：032→033近手前遮远掌仍让低杆核心从指后读出；火焰落真柴头，不混入远指，和侧管的实际前后关系单独看；头颈胸臂动作、桌盒薄影连续。035止，036不存在。

## 最小清单

RUNTIME_ROWS.json共36行：3新JS、3张033原层PNG、30旧层复用76ff15e0既有blob。033作者原层同批上传按同blob只传一次。UPLOAD_ROWS.json仅加轻量验证，不复制整母/长旧证据/拓扑图/影片。固定1822灯helper与共享helpers均不改。

验证：npm test；python verify_F033.py /path/to/astra_s08_first_mother_20261018_1433。源像素/几何检查不代表实际Canvas通过。
