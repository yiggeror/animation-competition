# F031 唯一 call07 局修 · 手电候选已取，整态衣片待审

本轮严格 **1次调用／1原件**，没有全图尺寸重抽。031累计 **7次**（前6次原件／提示词未改），本段含026累计8次，全S09累计12次。历史 `../requests/d06_call07_arguments.json` 从未执行；实际执行的是本目录 [call07参数](requests/call07_arguments.json)、[完整提示词](requests/call07_prompt.txt)，完整工具返回同目录`call07_raw_return.json`。

先看 [三阶段对照](qa/three_stage_comparison.png)、[1280×720候选](qa/F031_1280x720_pending_clothing.png)。本轮仅以call05上段平移下67px的原像素预摆为单一画稿源，向原生工具开放 [接缝／旧背景mask](masks/native_seam_and_vacated_background.png)。实际接缝大多被握手遮住，最终只取外露红筒纹 **611个返回像素**；没有改灯头、完整尾盖、双手、尺寸或姿势。旧上段透明区保持透明，其他原生返回变化全部舍弃。

[原始返回PNG](originals/d06_call07_raw.png)为1672×941，SHA256 `082ae4ac5c1aa4db58007e49704cc44a9a90eb0f90eedb1afca6c3f6972ebaa8`，与完整返回base64／宿主原件逐字节同。局部采用结果是 `candidates/d06_preposition_seam_locked.png`，它仍含call05旧头身，**不能直接作为母态**。

`candidates/d06_raw_locked_pending_clothing.png`与注册版是恢复头身的待审副本：d05锁母为底，[动作域](masks/action_domain_final.png)包含旧新双臂／袖口／手电及其清除范围；[头颈与衣领保护域](masks/protected_mother_head_neck_collar.png)强回锁母。已实算：原生修补mask外0改动、动作域外0改动、保护头颈／领口0改动，两手实际像素及灯头／完整尾盖逐值保留。详见 [数值与来源检查](qa/measurements_and_lock_checks.json)、[动作域叠图](qa/action_final_domain_overlay.png)。

**整态还未通过。** 作者及6.1sol实看发现：旧臂移开露出的衣片，在d05本来被遮住，没有可直接恢复的同位锁母像素；call05可填露出区域，但白点／裙褶与原衣片存在接合偏差。当前胸前白点和旧臂下衣纹接点仍须审，未把羽化或文件存在当作修好，也未扩大采用漂移头身。没有为衣片追加第二次生成；037／042均未画。Astra可先独立审手电局修，再裁定缺源衣片如何补。

实际人工尺寸复核：完整轴约 **375±8raw**（标点估376），灯头径 **128±5raw**，完整尾盖径 **83±4raw**；盖缘到实际掌缘净空 **60–65raw**，沿既定等比注册约 **38–41px**。相较锁母约381raw轴，误差在人工估读范围。F000尾盖受遮，可见44不是完整径；旧2.29px手部余量撤回。

[037／042新接触施工图](reference/F037_F042_actual_size_contact_targets.png)与[坐标表](reference/F037_F042_actual_size_contact_targets.json)按本次完整实际轴和尾盖推算：左掌固定；037筒及近握手上收20注册px，净空约59注册px；042相对031下移约62raw，使尾盖外缘触掌。灰色都是技术符号，未来前臂／袖口须按完整链重画，不能刚移整臂。**先031整态通过才037**，这张施工图不等于许可画042。

[build_delivery.py](build_delivery.py)可重放局部采用、显式锁母、既有等比注册和技术对照，并重新跑全部像素断言。无镜头／全片渲染，无代码人物，无新服务／API；S07未在本轮同时调用。
