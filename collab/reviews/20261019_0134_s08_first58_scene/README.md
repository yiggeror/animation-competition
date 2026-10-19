# S08 first58

入口s08_first58_scene.js，1920×1080、24fps、58/24秒。基线e94e1f19894dba379f79533dd6b263e7509cff2f；只新增053×5（53–57），058+全部入口拒绝。053人物/眼向双审允许精确复051/046，原母7722c855…385ec2及三层不改，无新PNG；2383根/57差继承合同见来源回执。

## 柴灭、原细烟、芯火不断

从frame053首样开始match m=0；其emit、light和glow随原条件全停。固定芯火/两glow/照明/冷蓝底仍用原值，w=.55。桌盒1665/薄接影、原低杆/罩高、人物层序和相机均保持。

烟代码来自固定0c215550的js/anim/s08.js：age=t−2.2，0<age<2.5，三条stroke主体逐字节复制。只将原q=S(M.head)接为真实屏幕药头A.head=(1350,782.572972972973)，并添加frame>=53门控；不改全局时间，不放大、不另加粒子或烟团。原height=60+age*140、width=3+k*4+age*6、alpha=max(0,.22*(1−age/2.5)−k*.05)。053/057整数采样高61.1667/84.5px，首线alpha .219267/.2046。完整5帧字段见TEST_RESULT；原文注释与持续时长有歧义，本包严格按原代码age<2.5，不推测后续烟结束点。

旧53的212子采样、绘制/光/glow/全部火焰及ctx命令不变；51旧PNG全字节相同。灭柴前红测确实失败，加入053门控后通过。新五帧烟的全部Canvas指令对照原公式通过，仍不是实际光栅化。

## 只渲新增5帧

```sh
node tools/js/frames.cjs collab/reviews/20261019_0134_s08_first58_scene/s08_first58_scene.js build/S08_first58_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 2.2083333333333335 --to 2.4166666666666665
```

输出00053.png–00057.png。旧53实际PNG须由原云首53缓存核SHA复用，不以本包静态测试代替旧53或新烟实际审查。新增实际门：052→053柴火及贴身暖光确实撤去、细烟从真实药头生出且自然上升、芯火不闪断；远杆座/侧管前后/单盒保持。本包新增实际Canvas0帧。

RUNTIME_ROWS54项：2新JS＋复用layer_contract.js旧blob＋51旧PNG blob，源层无需复制上传。npm test及python verify_F053_reuse.py /path/to/astra_s08_first_mother_20261018_1433为静态/像素检查。全部最终SHA256SUMS最后统一生成，首53包不改。
