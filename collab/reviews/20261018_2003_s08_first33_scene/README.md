# S08 首33候选

入口 s08_first33_scene.js；1920×1080、24fps、33/24秒。固定first30源25705ee43f0a7e169cd9cc4ba05d50a341d6f3b1，旧30实际双审记录e3cfa91e25dc81bf7c1cf18e728800390fb5896b。此次只加唯一030×3（30–32），033+所有入口拒绝。新030尚未真实Canvas；作者角色静态/两底6f双审与实际接景验收分开。

030唯一SHA ef53ba49d805d2a9eb2cf934f62b2098a07e924250fcbbd5070cb33fcbba6bc8。采用作者按030实际转躯干/袖肘重分的SEALED三层，没有套027旧mask。三层互斥RGBA重建精确，盒1665只table_box一次，两肘在981以下0像素。真近手7843、近远端硬保护6370、完整远手/透明座17750均与最终锁档RGBA相同且在正确层；已释放的1006远手外部alpha0区允许近手前遮，旧183肤领不恢复。运行中人物x0/y0/sc1，不旋转/缩放/拉伸补动作。

前30的120子帧合同、30帧绘制光火、27原层字节、全部绘制函数源码回归全同，旧包45条SHA256SUMS不变。030仍低杆lift1/角−.35/总升罩83.24324324324324；杆端(1233.9532049682696,766.8943738423919)不动，灯芯0。火头(1148,717)、露木出口(1116.881786,751.418843)取最终真手合同，原火光公式只随真实火根。contract真灯芯顶点仍(1415,794.572973)，不得误接helper return代理793.059459。

层序仍lamp/凳/body/桌前沿/table_box+原contact/arms；真低杆在原透明握座后，图内无杆。桌位置、前唇、盒薄影参数不改。

## 最短实际渲染

```sh
node tools/js/frames.cjs collab/reviews/20261018_2003_s08_first33_scene/s08_first33_scene.js build/S08_first33 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first33_1920x1080_24fps.mp4
```

只新增030–032（沿用帧编号，不生成全片mp4）：

```sh
node tools/js/frames.cjs collab/reviews/20261018_2003_s08_first33_scene/s08_first33_scene.js build/S08_first33_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.25 --to 1.375
```

单帧030：

```sh
node tools/js/snap.cjs collab/reviews/20261018_2003_s08_first33_scene/s08_first33_scene.js build/S08_F030.png 1920 1080 1.25
```

实渲门：旧000–029无损保持；029→030转躯干/抬近臂/真实腕布缝与头肩一致，远手仍扣低杆，光火跟随真实火根，近手前遮合理；两肘全在桌前唇上方，桌盒单影不漂。032止，033不存在。

## 最小上传

RUNTIME_ROWS.json共33行：3新JS、3张030新层PNG、27张旧层复用25705既有blob。030作者原层若同批上传按同blob去重，只传一次。固定1822灯helper不变。UPLOAD_ROWS.json包含轻量验证证据，无整母/拓扑图/影片重复。

旧固定tree60路径由协调GitHub逐SHA与partner读回确认；本地原30行上传表和45条checksum全过，不为clone缺树重复补取。验证：npm test；python verify_F030.py /path/to/astra_s08_first_mother_20261018_1433 /path/to/astra_s08_f027_parallel_20261018_1812。
