# S24首母 · 同raw棕发最小回色，待Astra锁精确版本

唯一待锁文件：[F000_hair_corrected_rgba.png](candidates/F000_hair_corrected_rgba.png)，1024×1536 RGBA，SHA256 **`0485c6fe2ee6ec05d762a6b1c531ed9764e7e77223b6cce455b54f50f99eff22`**。RGBA像素SHA在[数值核验](correction_validation.json)。原始生图仍为上一包`originals/S24_F000_call_001_raw.png`（SHA`35bb55ea…2281`），原件/旧候选/提示词和工具返回均未修改，本轮生图0。

按[双审反馈原文](astra_feedback.md)，身份、清醒左下视线、闭口、颏颈和短垂辫已获Astra双审；这里只改三处连续棕发语义域的底色，不重生首态、不全图压暗。[固定母色/修前/修后](qa/00_master_before_after.jpg)、[冠发与两尾分别对照](qa/01_three_hair_regions_before_after.jpg)、[精确改动与保护域](qa/02_changed_teal_line_purple_highlight_orange.png)、[修后三底](qa/03_corrected_three_backgrounds.jpg)已实际查看。作者未见新的发色断层；脸颈、衣裙、表情、发形完全保留。

以锁定`assets/chars/x13/F000.png`（SHA`91715601…850`）的三个对应内区取样：冠发底色减RGB`[6,5,6]`，近尾`[6,4,5]`，远尾`[2,0,1]`，只在非保护区域局部羽化。近尾对应“母稿画左→S24画右”，远尾反向对应，未把屏幕左右直接当近远关系。修后中位数Δ分别为`[0,0,0]`、`[0,1,0]`、`[0,0,0]`；相同ROI材质均值最大单通道差2.78161，均在±4内。ROI、像素数、均值/中位/P10/P90和种子坐标全部保留，统计不冒充全图均色一致。

三个单独种子连通域、深线/窄暗线与抗锯齿保护、高光保护、实际修正权重和最终变化mask均在`masks/`。[检查结果](correction_validation.json)：改动212752像素，RGB最大降量`[6,5,6]`，无亮向改动；alpha、线稿保护、高光保护及三个语义域外变化像素均为0。包括脸/颈/耳/眼/口/红发结/衣裙在内的域外像素原RGBA逐点相同。原始alpha含淡晕保持不变，没有借修色清边。

**B配准按Astra意见采用**：整层`.70+(590,20)`，1920×1080场景；[参数JSON](registration_B.json)和[中性底图](qa/04_B_registration_neutral_NOT_SCENE.jpg)只作注册诊断，未真实接景。按alpha≥248实体顶端重测余量92.8px，与反馈约91px属同一近似范围；头比旧构造约大14%，后续回头/抬颏须守画幅，旧尺不是精确成图尺寸。

[完整局部修正脚本](tools/correct_hair.py)与[运行输出](correction_run.log)齐。仅对保留原件生成新版本，未改生产分支/公共模块/EDL/声音/ready。F006/F009/F012仍未启动；请Astra先锁以上**精确SHA**，后续派生使用修后母态，旧浅色母仅作历史。
