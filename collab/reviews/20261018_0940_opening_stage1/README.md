# 开场阶段1：7张可接候选、k05盘接触副本、下一组参考

只新增collab候选；主实现、docs、assets未改。参考门来源：dee8414a45906b2474fbcb335306c54e89171d81，Opus1206141dbdd8abb850f9d5498c046230365ca243已放行。

## 直接接入
- S03_C/F065_candidate.png：F065–073（9帧）；F074_candidate.png：F074（1帧）；F075_candidate.png：F075（1帧）；F076_candidate.png：F076–078（3帧）。F058–064仍原k06；F079–095仍原k07。4次真实生成；眼眉局部接回，最终alpha精确锁k06。原k06仅右补1透明列1671→1672，无人物缩放。最终SHA见manifest与独审末尾，旧alpha版本只留审计，不能接错。
- S02a_blink/final/S02a_F013.png、F014、F015各曝光1帧。F016精确复用原focus，不能把半闭拉长代替缺帧。3次真实生成，逐张由上一合格图派生，眼mask外RGBA零变。F023/041/044仍在制作。
- S03_k05_plate/S03_k05_fixed_plate_candidate_v4.png是原F044/k05副本，SHA256 42c5b9537fc400138c100c4ec6eebc4d1cf645b6c00a959ac2d9536dd88e26d2。先将原k06空盘原像素下移6px到约453,918，原k05手瓜/臂不移；再1次局部生图只补原被旧盘沿遮挡的瓜底与接触。v4对v3仅2092像素改动、bbox[364,899,474,924)，alpha及mask外均未改。独审实际确认接触和边缘。v3保留失败截底证据，不接入。

上述是静态候选/邻接通过，实际曝光MP4待审。请先按原曝光接这两小段并交实际增量MP4；不必等完整S03/S02a，也不要补长停帧冒充缺口已完成。S03 A4与B5仍制作，B已经使用通过的v4端点。旧k04/k06盘仍有约2–6px小残差，本次不宣称全20态盘位完全锁定，请接景时统一已有盘层或明确残差，不能重新引入原40px大跳。

## 下一组参考门
next_reference_proposals/README.md和三张qa图为S05a九态、S03a六脸态+一手瓜提案，尚未开画。请优先确认：
1. S05a F010解释为意识到此前已黑屏，不再第二次熄光；两次按键肩顶/落与疑惑竖小圆口，撤掉代码笑嘴。时表不改。
2. S03a脸只左偏一次再回，仍看画外手机；可以先放行脸链。独立右手瓜资产沿未咬k07，但新镜头纵深角度尚未冻结，不能靠旋转侧面旧手或虚焦冒充。请定前景右下入画方向与托持角度。

## 溯源与复现
每子目录保留实际生成原件、实际提示、显式mask、候选和短QA。全包文件大小/SHA256/Git blob列manifest.json。S03_C inputs为真实裁剪输入，analysis/pre_alpha_lock为独审前版本；RGB与最终一致，alpha锁定已增量实审，均不可作新候选。
原锚固定在fb0f系列交付和本轮dee8414参考包，source_manifest列确切commit/path/hash。S02a BLINK_MANIFEST内绝对本机路径仅是生成履历，实际包内相对路径见BLINK_DELIVERY。
S03_k05_plate/compose_plate_copy.py为实际执行记录，源输入按脚本原相对布局放于../astra_s03b_painted_pilot_20261018/refs/painted/，取原k05/k06，SHA在plate_fix_v3.json。它不是无依赖安装脚本。compose_contact_patch.py依赖本目录已附v3与call01实际原件，可独立复现v4局部接回。元数据的pending状态保留生成时原文，最终是否通过以independent_review末尾为准。

独审INDEPENDENT_REVIEW按版本保留旧结论；最终C4必须使用其09:41 alpha锁定四SHA，k05只v4通过。未宣称原速主观自然或完整动作完成。
