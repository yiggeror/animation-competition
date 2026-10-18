# S08 首30候选

入口 s08_first30_scene.js；1920×1080、24fps、30/24秒。前27 source a4b00a05、真实9a6b01f7已由协调双审通过。此次只加唯一027×3（27–29），030+全部入口明确拒绝。新027尚未真实Canvas，静态结果不能替代实际验收。

唯一027原母SHA 2dc0ee2bc06b4b872e0f79cbf4c1bd19b2ccaa160cba9b5feefd45f2a8e268ac。三层取作者最终SEALED版：body d6ca9051、arms 5d5751fe、box33803ac0；原像素互斥RGBA重建精确，盒1665只table_box一次。人物x0/y0/sc1。近手7631像素相025(+6,+3)，远手和完整透明座18756像素相025(−8,+16)逐RGBA同；最终guard释放183近端非玉镯旧肤领接回新前臂，不恢复旧mask。

000–026的108子帧合同、27帧绘制/光火、原24层字节、全部原绘制函数源码回归全同。原first27包SHA256SUMS全部不变。027低杆lift1/角−.35，端点(1233.9532049682696,766.8943738423919)，罩总升83.24324324324324。与人物换张同帧到位，不插值拉手；高→中→低→高缓存不串态。真实火头(1082,797)、可见木出口(1054,834)，原光火公式跟随。灯芯始终0。contract真灯芯顶点(1415,794.572973)不变；后续030+勿使用helper return wick代理793.059459。

层序仍lamp/凳/body/桌前沿/table_box+原contact/arms；真独立低杆从透明握座后透出，人物图内无杆。桌位置、前唇、盒薄接影参数均不动。

## 最短真实渲染

```sh
node tools/js/frames.cjs collab/reviews/20261018_1940_s08_first30_scene/s08_first30_scene.js build/S08_first30 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first30_1920x1080_24fps.mp4
```

只新增三帧027–029：

```sh
node tools/js/frames.cjs collab/reviews/20261018_1940_s08_first30_scene/s08_first30_scene.js build/S08_first30_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.125 --to 1.25
```

只先核027：

```sh
node tools/js/snap.cjs collab/reviews/20261018_1940_s08_first30_scene/s08_first30_scene.js build/S08_F027.png 1920 1080 1.125
```

实渲门：000–026无损帧对9a6b01f7保持；026→027杆转/升罩/手扣同步，旋钮从真指后读出，近柴火根(+6,+3)跟随；盒仍落桌/单影；029止，030不存在。

## 最小上传与验证

RUNTIME_ROWS.json共30条：3新JS、3新027层PNG、24旧PNG复用固定a4b00a05的gitblob。若027作者原层包同批上传，按同blob只传一次。固定1822灯helper及共享helpers不改，不上传整母/静态拓扑图/影片。UPLOAD_ROWS.json含轻量证据。

验证：npm test；python verify_F027.py /path/to/astra_s08_f027_parallel_20261018_1812 /path/to/astra_s08_first_mother_20261018_1433。
