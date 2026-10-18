# S08 首27帧候选

入口 s08_first27_scene.js。1920×1080、24fps、27/24秒。000–022保留已实审首23的原图、动作、机械初位、光火参数与绘制指令；023×2扣高杆，025×2扣中杆；027及以后所有入口抛错，无延长停帧。

023原母 SHA dc35d227078f37e18340635c95f721a5b8495ecbb87b802df51447d375987e47；025原母 SHA 25e5ff2a37421bc90bbbaa3650e912def85d64fea1ee7a5cafa1a3c98f689cae。仅引用原像素互斥三层，不复制整母。灯/凳/body/桌前沿/table_box+原contact/arms，人物x0/y0/sc1。盒1665可见像素只画一次。

000–024 lift0角−.85；025–026 lift.5角−.6；升罩41.621621622px，中杆端1242.151547685,750.952730291。独立原灯杆在原手指后，透明握座保留，没有额外旋钮或烘进人物的杆。灯芯始终0。contract.js 的 LAMP_WICK=[1415,794.572972972973] 已是灯芯fillRect(-21,-226,42,6)真实顶边中点，与首23原值完全一致。旧helper返回的 wick=[LX,LB-228] 则映射到793.059459，属于代理值。后续030+必须沿用已冻结真实顶点(1415,794.572973)，不得误接helper返回代理值。本包没有点芯。023真实火根1070,791/木出口1042,828；025为1076,794/1048,831，原光火公式不变。

静态通过：24层SHA、两新态RGBA精确重建、完整原手含alpha0握座保护、首23的92子帧合同与23帧绘制/光火一致、高→中→高缓存无串态。未运行真实Canvas。原first23和局部灯修包校验全同。源证据原文状态保留；025最终唯一锁由协调与作者双审通知确认。

## 最短真实渲染

```sh
node tools/js/frames.cjs collab/reviews/20261018_1900_s08_first27_scene/s08_first27_scene.js build/S08_first27 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_first27_1920x1080_24fps.mp4
```

增量仅新4帧（保留原编号00023–00026，不生成全片）：

```sh
node tools/js/frames.cjs collab/reviews/20261018_1900_s08_first27_scene/s08_first27_scene.js build/S08_first27_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 0.9583333333333334 --to 1.125
```

首帧/025快照：

```sh
node tools/js/snap.cjs collab/reviews/20261018_1900_s08_first27_scene/s08_first27_scene.js build/S08_first27_F000.png 1920 1080 0
node tools/js/snap.cjs collab/reviews/20261018_1900_s08_first27_scene/s08_first27_scene.js build/S08_first27_F025.png 1920 1080 1.0416666666666667
```

实渲门：000–022无损帧与3703140f来源对照；022→023真手扣高杆；024→025同帧杆转罩升、真实旋钮在指后可读、火根跟随(+6,+3)；全段盒底接影和前唇顺序不变。完整27帧终点1.125秒。

## 最小上传

RUNTIME_ROWS.json列27条：3新JS、3张025层PNG、21张旧层复用Gitblob。025图片如随stage61原层包已上传，直接复用同blob，无须再传。固定灯helper复用5783690f，无需改共享js/code/s08.js。UPLOAD_ROWS.json另列轻量验证证据，不上传整母/拓扑QA/影片。

验证：node test_module.mjs；python verify_F023.py /path/to/astra_s08_first_mother_20261018_1433；python verify_F025.py 同路径。
