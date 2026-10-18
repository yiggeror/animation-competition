# S08 首38候选

入口 s08_first38_scene.js，1920×1080、24fps、38/24秒。基于固定first36源2a8fcb919cc4efe59169be80650d10621427ef25，只增加036×2（36–37），038+所有入口拒绝。正式41态表为033×3、036×2、下一038，未补持帧。旧first36真实源2417653ffc6a0beb5c2036a5160b2b1bd0508334由协调另行审查；本包没有产生新实际Canvas。

036唯一母SHA 6ee3d4ccf88650496ce97f8709642fb3b5a228fd0ec1a5e5fd4efc50fac42753。采用作者更正后的三层，重建母RGBA全等、alpha互斥。单盒1665可见RGBA/alpha域与033全等，底970；原033周边483像素仍在body，不能移到桌前盒层制造新投影。原contact参数不动。作者修复近手复用档53旧蓝领点，distal6435像素0改，运行母不改。整条新近前臂遮挡远手，不能用两个独立手档代替完整前臂重建。

旧36所有144子帧合同、36帧绘制/光火、33旧图层字节、原封包SHA全部回归。scene自async function bg()起逐字节不变；角色x0/y0/sc1，不作运行形变。新增036火根(1335,785)、木出口(1297.4057137582938,812.1968682383957)。低杆lift1/角−.35、罩总升83.243243、芯0；148像素低杆盘与033逐RGBA相同。灯芯绘制真实顶点仍(1415,794.572973)。

层序保持lamp/凳/body/桌前沿/table_box+原contact/arms，最后绘制原火焰。近手/柴/火越侧管按前景深度交越，不能称2D全程净空；本包按正式换张曝光，不插值人物。新增实渲门是035→036整胸臂动作、真实火根/侧管前后读法、远手透明扣座、单盒薄影、芯暗。

## 最短新2帧实际渲染

```sh
node tools/js/frames.cjs collab/reviews/20261018_2157_s08_first38_scene/s08_first38_scene.js build/S08_first38_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.5 --to 1.5833333333333333
```

frames.cjs按Math.round(seconds*fps)取半开帧区间，此命令只输出00036.png和00037.png。全片如需：

```sh
node tools/js/frames.cjs collab/reviews/20261018_2157_s08_first38_scene/s08_first38_scene.js build/S08_first38 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first38_1920x1080_24fps.mp4
```

## 最小清单

RUNTIME_ROWS.json共39项：3新JS、3张036新原层PNG、33旧层复用first36固定blob。036原层若同批作者包已上传，按相同blob复用。UPLOAD_ROWS.json仅加轻量验证/合同，不复制整母、长旧证据或影片。共享helpers和固定1822灯helper均不改。

验证：npm test；python verify_F036.py /path/to/astra_s08_first_mother_20261018_1433。静态/命令/像素检查不代替实际Canvas。
