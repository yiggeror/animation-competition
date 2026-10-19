# S20 F000：只含正确臂链的最终四图输入门（0新调用）

已合并Astra独审最终补充，**四图方案替代额外身份材质裁片方案**。本轮只准备输入，未执行模型请求、未预约第三次调用、未制作后态。历史仍为2调用/2原件，当前0在途。

## 实际生成白名单：仅以下四图

| 顺序 | 实际文件 | 用途 |
|---|---|---|
| 1 | [唯一正确全图target](inputs/01_F000_only_correct_pose.png) | 1672×941；已清旧臂并置入完整正确双臂体量，近L高位镯掌、远R低位裸腕；唯一姿态底 |
| 2 | [该target肩至双掌直接4倍放大](inputs/02_target_shoulders_to_palms_4x.png) | 从第一张`[875,235,1220,485]`原像素裁出345×250，直接复制像素至1380×1000；无重画、无透衣拼版、无新标记 |
| 3 | [正确双臂透衣体量](inputs/03_correct_arm_xray.png) | 独立说明远R上臂和肘藏在躯干后；不是输出时的透衣效果 |
| 4 | [唯一白域mask](inputs/04_edit_white.png) | 1672×941；白可完稿、黑保护；只送这一种黑白语义 |

第一张与5ce9da50已审正确target逐字节相同，SHA256：`a6d23f92bd8eef585881f1c674c2cbafe5c42b7a9a6696437b72430ae0cefa0a`。它是已纠正姿态的施工输入，尚非新生成的完成画稿。第二张的[直接放大变换](enlargement_transform.json)可逐像素复核。

[实际四输入、尺寸和SHA](input_manifest.json)、[完整准备请求](request_prepared.json)、[完整提示词](prompt_zh.txt)齐。prompt首句严格为：**“把第一张已有正确臂链自然完稿。”** 第二张只作放大，第三张隐藏臂不画透；不重新设计姿态。

call001/call002完整原件、带旧臂的任何对照图、额外身份材质板、反相保护图均不在`referenced_image_paths`，也不使用会话最近图片参数。`inputs/`中恰好只有上方四文件。

## 清除证据与本地保护

[旧臂原件→清空旧臂占区→置入正确连续体量的三步对照](qa_only/old_arm_removal_comparison.png)只供QA，**不送模型**。中图同时清掉原近袖下的小块旧上臂，保住双掌/单镯/四前杆。最终姿态完整见[正确target灰底](qa_only/only_correct_pose_full_gray.png)。

双掌、握指、玉镯、四前杆及孩子保留call001原像素；奶奶头颈、腰腿脚、孩子尺寸和原抓持关系不变。原raw只留本地用于保护和本对照，不再作为模型参考。白域外必须在未来合成时复用原RGBA；[本地反相保护图](masks_local/protect_white.png)不送模型，避免相反黑白语义干扰。

[本地保护合同](local_protection_contract.json)保留原raw的真实路径及SHA。未来返回先核严格1672×941、完整近L/远R肩袖—肘—腕、旧边与接腕，再按白域局部合成；不能只相信模型遵守参考mask。

call002的1671×941原件及完整请求继续保留在旧门，未拉伸、补列、裁切或改字节；不作新图注册源。颈侧减暖和孤立alpha清理未做，原216帧/切点/镜头/道具关系、旧门、生产代码与共享文档均未改。

## 审查与复现

[两次指示及最终四图边界](review_directives.json)、[作者实际看图记录](author_visual_review.json)、[像素/白名单验证](verification.json)、[本门SHA清单](SHA256SUMS.txt)齐。

在仓库根目录可重建静态输入及未提交请求：

```bash
python collab/reviews/cloud_s20_20261018/F000/arm_correction_002_no_oldarms/prepare_inputs.py
python collab/reviews/cloud_s20_20261018/F000/arm_correction_002_no_oldarms/prepare_request.py
```

这些命令不调用模型，不启动场景或全片渲染。当前状态：**最终四图与完整prompt待Astra输入门审查；不立刻重试。**
