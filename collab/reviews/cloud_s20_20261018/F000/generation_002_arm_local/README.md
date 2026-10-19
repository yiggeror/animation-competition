# S20 F000 call002：唯一双臂局修未通过，未回贴

Astra主审和独审通过 `5ce9da50b92eac9062e808a335c4f0b2f5b08995` 的实际五输入及完整提示词后，原样执行**一次**局修。提交前0在途；本轮1调用、1原件、0重试、当前0在途；本云S20累计2调用、2原件。颈色/孤立alpha未处理，后态0调用。

**本次不通过，不得采用为修好后的F000。**

- **双臂归属未纠正**：高位镯掌仍接远侧臂；低位裸腕仍经近肘接近肩短袖。原错误整条臂链仍在，未实现“近L→高掌、远R→低掌”的已审target。
- **尺寸不符**：PNG IHDR与Pillow均读得 **1671×941**，冻结画布为1672×941。未推测少列位置，未缩放、补列或裁切。
- 因结构和尺寸门失败，**未执行白域回贴、没有合成候选/最终人物图**，不登记ready。原始raw保持原字节，不用施工target冒充绘图结果。

## 原件与直接证据

[唯一原始PNG](S20_F000_call002_arm_raw.png)，SHA256：`9f8edf0f17d5aac7ec425bb74258e168a80f0aad096c56a3efd4f307b6ce98bf`。原工具文件 `/workspace/generated_images/exec-bc1edef4-c3c8-4968-b27f-3e49d4caf5e1.png` 仍保留，仓库副本与完整工具返回的图像载荷逐字节一致。

- [call001原件／已审target／本次失败raw并排实看](qa/approved_target_vs_failed_raw.png)
- [完整肩袖至双掌放大](qa/raw_shoulders_to_palms_3x_QA.png)
- [高掌仍接远侧臂](qa/raw_high_wrist_to_far_sleeve_3x_QA.png)／[低掌仍接近肩臂](qa/raw_low_wrist_to_near_sleeve_3x_QA.png)
- [全身灰底诊断](qa/raw_full_gray_QA.png)、[尺寸实测](dimension_inspection.json)、[逐项失败审查](author_visual_review.json)

QA图的裁片/整数放大仅供检查；没有对原始PNG进行注册或尺寸修正。未声称失败raw的孩子、两掌或四前杆与源逐像素一致。全部原件和已审输入保留，源图及生产素材不改。

## 完整请求和五输入

[Astra放行原文](authorization.json)、[提交前核验](preflight.json)、[实际完整请求](request_submitted.json)、[完整提示词](prompt_local_edit_zh.txt)、[完整原始工具返回](tool_return_original.json)、[当前单次状态](status.json)齐。

[五输入快照索引及SHA](submitted_input_snapshots.json)对应 `frozen_inputs/` 的五张实际文件，顺序为原call001、已审target、白域、保护域、双臂透衣体量；[冻结输入清单](frozen_gate_input_manifest.json)保留提交前的历史状态。调用参数与已审准备请求逐项相同，没有更换图或改提示词。工具为 `image_gen.imagegen`；底层模型版本未披露。

工具返回没有满足已审目标，尺寸少列原因未知，未猜测模型内部原因，也未追加尝试。以[验证记录](verification.json)及[本门SHA清单](SHA256SUMS.txt)核对资料完整性；“资料完整”不代表“图像合格”。

目前仅交这张失败原件供Astra决策；局修未完成，后态继续暂停。原216帧、切点、旧门及旧原件、共享留言、生产代码和ready均未改。
