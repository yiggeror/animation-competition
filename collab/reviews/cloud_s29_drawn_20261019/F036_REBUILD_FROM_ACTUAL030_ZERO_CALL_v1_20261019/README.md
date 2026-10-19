# S29 新036：从成功030实际形体重建，零调用短门包

本包纠正前次输入构造根因：旧准备只检查成功030，却从旧拼接036造目标，导致夹点下退。本次人物与高布峰直接取成功030唯一原件（SHA256 `0c182aa0d62acf8647daa316e06cdb4bfdd9ebd6c2e6c02f1b0e2f8065ffd4e5`），共同画幅固定1024×1536；头胸、近裸臂、下身与凳子不整体平移/缩放。完整远臂用连续实际像素技术探针表达微收，避免分块肩/肘接缝；此为绘图参考，**不是新native绘图或成片人物**。

先看共同尺度与实际接触：

- [实际030与新036同尺全身/接触对照](audit/ACTUAL030_NEW036_BODY_AND_CONTACT_COMMON_SCALE.png)
- [整远臂、同夹点与高布峰同尺对照](audit/FULL_ARM_PINCH_PEAK_BEFORE_AFTER_SAME_SCALE.png)
- [固定真实尾羽的遮盖前后同尺近图](audit/TRUE_TAIL_BEFORE_AFTER_SAME_PROPS_SAME_SCALE.png)

唯一预定四输入，顺序固定：

1. [唯一完整新036技术目标](inputs/01_ONLY_NEW_F036_FROM_ACTUAL030_COMPLETE_TARGET.png)：由成功030完整形体构造，夹点向躯干内20px、微升3px；保留高峰与宽布面，只小翻前唇。第一图的原生人物画幅位于外框[20,80]。
2. [头身份与衣布内部材色裁片](inputs/02_024_HEAD_AND_INTERNAL_MATERIAL_CROPS_ONLY.png)：沿用已过的024裁片原字节，无旧完整姿态或臂手。
3. [同目标整远臂与不透明翻唇放大](inputs/03_SAME_TARGET_WHOLE_ARM_AND_OPAQUE_LIP_ENLARGED.png)：同一新目标，右侧放大真实外羽与前唇T交接。
4. [新完整移动域及小遮尾域](inputs/04_NEW_MOVEMENT_DOMAIN_AND_SMALL_TRUE_TAIL_COVER_ONLY.png)：白域覆盖当前完整远臂和棉布面，仅开放这一次少量外羽遮挡；黑域保护近裸右臂、原偶其余部分/直杆、头胸与下肢。是语义参考，不是已执行的inpaint参数。

完整预定请求在[逐字提示词](requests/PROMPT_PLANNED_NOT_EXECUTED.txt)与`requests/arguments_PLANNED_NOT_EXECUTED.json`；四图SHA在`requests/FOUR_PLANNED_INPUTS_SHA256.json`。实际030整图仅存audit作为构造/审查来源，**不额外进入请求**；旧整母、机位人物、旧拼接036和失败036均不进入新请求。

共同坐标同时核近掌/胸肩/下身与真尾羽。真偶组用一个由近扶颈点及8处胸肩/下身对应点约束的等比旋转映射进入实际030画幅；人工标点不确定约15px、参考拟合RMS约10.18px，仅供本技术接触目标，不宣称正式接景注册通过。两参考态始终复用同一真实偶/四杆RGBA层，未移动偶制造覆盖。原030含生成道具的部分只在明确mask中换成技术布材底后接真实原件；所有改动域和来源随包。

当前前唇实际遮掉141个外羽/AA像素，其中保守黑羽核心44/843；余约95%核心和全部不透明偶身/杆像素保持。计数只是构造核验：实际近图须能读出羽线在不透明前唇处终止。`qa/ACTUAL_PIXEL_AND_CONTACT_CHECKS.json`记录真实合成像素、身体保护和白域覆盖；不拿文件存在、计数或源文件同一性代替动作判断。

`build_actual030_reference.py`可重放本技术包。分块试探曾留下接缝的开发候选及脚本留在audit，明确不进入请求。最终目标使用连续实际030整臂探针，原生绘图仍需在短门后完整重画，不采用技术变形作为画稿。

**当前0新请求、0新原件、0重试，待Astra实际四图短门后才单次定向修036。** 本包不改变此前024/修后030的有限门或失败036原件，不改共享生产代码/文档；S28已成192保持原样。
