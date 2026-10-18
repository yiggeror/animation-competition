# S10 F000 同原件定向修复 · 锁母候选

唯一取图：[`candidate/F000_repaired.png`](candidate/F000_repaired.png)，**1920×1080 RGBA**，SHA256 `0e231c39834a557ea73cc9af146b6ebf7c35dac4f160c83ae2242f270b0c07c6`。作者已实看黑／白／灰底、发顶与下颏锚点、原尺寸下胸衔接；交Astra最终锁母，尚未生成其他姿态。

先看 [黑白灰底与锚点总览](qa/F000_black_white_gray_and_anchors.png)，再看 `qa/F000_on_black.png`、`F000_on_white.png`、`F000_on_gray.png` 的原尺寸副本和 [下胸近图](qa/chest_join_native.png)。衬底副本只供检查，不能拿来替换透明候选。

## 同raw，整张等比，头颈不重绘

原件仍是 `../F000_first/originals/F000_call01_raw.png`，SHA `9f2ef4b4…53dd4c`，未改动。

全图只用一次统一仿射：`x'=0.918x+171`、`y'=0.918y+114`，画布1920×1080。没有单独缩头、锚底、拉长颈或重画五官。Pillow RGBA BICUBIC按预乘alpha重采样。完整矩阵、逆矩阵及方法在 [transform_and_cleanup.json](provenance/transform_and_cleanup.json)。

- 参考源发顶y12 → 125.016；实际候选alpha≥128最上沿 **y125**。
- 源下颏y671 → 729.978；实际PNG在下颏ROI内独立查到黑线最低 **y730**。
- 源图底边到977.838；新增衣带严格只在 **y978–1079** 的两侧衣轮廓间。
- **候选y0–977的全部RGBA与清边后等比定位副本逐像素相同**；衣带掩码外改动0像素。头脸、眼镜、耳朵、发型、颈领均来自同一个已认可raw，没有采用局部回图的上方领／颈像素。

## 局部清边

复算源图4连通主域外为1069px／438连通域，与Astra补充相符。清理掩码只去孤立低alpha点与局部外缘高色差碎边，保护灰黑细发和左侧红珠。共2013px，实际被去掉的最大alpha为10；**源RGB改动0、alpha>24改动0、保护区改动0**。主体253／254保持原样，没有全图alpha<128硬切，也没有调整脸／颈材质。

实际清理和保护mask在 `masks/source_alpha_cleanup.png`、`source_hair_red_protection.png`。低alpha细发与正常抗锯齿保守保留，不宣称将所有弱alpha像素清零。灰黑发丝和左红珠在深浅底下均保持可见。

## 只补102行下胸衣带

按本次直接授权，**只执行1次局部衣带请求**。输入是1024×256的局部上胸裁片，不含头脸；上部少量原有颈／领仅作衣纹衔接上下文，最终没有取用。完整实际请求／prompt／输入SHA／返回元数据在 `provenance/cloth_call01_*`。

原始回图 [`originals/cloth_call01_raw.png`](originals/cloth_call01_raw.png) 为2171×724 RGBA，与工具原件逐字节相同。工具改变了裁片尺寸，先按原有衣纹统一配准（局部比例2.121213…及偏移见 `cloth_donor_registration.json`），只取对应缺失102行。新衣带外轮廓按原肩袖斜率延展，上口约x517–1399，画底约x470–1446；小幅逐行横向对齐只作用于新衣带。回图底端彩色杂像素没有落在采用范围内。

接缝的蓝布底色差在新衣带前48行内做平滑低频匹配，偏移RGB为(8,2,4)，白花瓣和黑线不做高频拉抹；脸、颈、原衣全部未改。花瓣／门襟线沿原有纹样继续，未添新领口或横向衣摆。第一次直接拼接有轻微色阶，保留 `qa/F000_unblended_band.png` 作来源证据，**它不是取图路径**。

实际检查见 [actual_candidate_checks.json](qa/actual_candidate_checks.json)：977／978行轮廓连续，主体alpha中位254→253，不是空洞；978／1000／1079行衣带内部均无低alpha洞。实看三种衬底未见明显的断衣白片或硬横线；衣带的最终美术接受仍由Astra锁母，不以数值门代替图审。

## 来源和重放

本镜累计：首F000全人物1次＋本次局部衣带1次＝2次图像请求；本次没有重生整个人物，其他曝光态0次。两次原始输出均保留。底层模型未披露，工具名如实登记 `image_gen.imagegen`。没有新服务／付费API／Blender／全片渲染，也未改共享实现／留言／ready／音轨。

在仓库根顺序运行可重放同一候选，不会调用图像工具：

```bash
python collab/reviews/cloud_s10_20261018/F000_repair/prepare.py
python collab/reviews/cloud_s10_20261018/F000_repair/register_donor.py
python collab/reviews/cloud_s10_20261018/F000_repair/compose.py
```

`authorization.md`保全本次两条原文指示。候选需要Astra锁母后才可派生024／027／033等关口，本包没有越门扩链。
