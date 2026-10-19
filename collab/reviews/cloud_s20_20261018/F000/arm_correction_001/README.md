# S20 F000：双臂归属＋低位签尾，零调用局部输入门

源为 `300840f48aaa8fec60f2392bc16beb28e0a963e1` 的[唯一call001原件](../generation_001/S20_F000_call001_raw.png)，SHA256 `de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330`。**Astra未通过原件的近远臂归属**，此前作者自查通过记录保留为历史，以本次返修门为准。原件只作为身份、受保护像素及真实握持来源，不能再照抄其错误臂链。

本轮只制作施工输入：**新增模型调用0、新原件0、在途0、后态0**；全项目本云S20历史仍只有call001一张。没有重抽两人、换镯、镜像或缩放孩子。本目录target是人工定义的局部连续体量参考，**不是新生成或可用于成片的角色画稿**。

## 先看三图

- [原件／纠正target／透衣完整双臂](qa/shoulders_to_palms_three_view.png)：近L从画面右侧近肩和近袖接高位带镯掌；远R从远肩与远袖后方，经躯干后完整上臂、肘及前臂接低位裸腕掌。透衣图显示真实被遮体积，成图不得画透。
- [双掌与四杆接触](qa/palm_rod_contacts.png)：两掌中心、握指、单镯、四根前杆保原像素；低位错误外露短尾已在target清除，正确终点藏在掌内，不强加可见尾。
- [全身灰底target](qa/target_full_gray_QA.png)：孩子、奶奶头颈和腰腿脚原像素保留。袖布和肤色平块是体量施工说明，后续局修须按原件恢复自然线条、衣褶/花纹和腕部过渡。

## 实际输入、白域及保护域

| 文件 | 含义 |
|---|---|
| [S20_F000_arms_target.png](S20_F000_arms_target.png) | 1672×941 RGBA实际target，完整连续双臂局部体量已叠到原件坐标 |
| [edit_white.png](masks/edit_white.png) | 白255可编辑、黑0保护；39,395像素，仅双肩袖、双臂连接及低位错尾 |
| [protect_white.png](masks/protect_white.png) | 上图严格反相，白255必须复用原件RGBA |
| [受保护双掌／单镯／四前杆](masks/protect_palms_bracelet_front_rods.png) | 具体接触保护域；与编辑白域不相交 |
| [完整双臂透衣体量](full_arm_volume_xray.png) | 用于看隐藏的远R上臂和肘；非成图图层 |
| [实际5输入与SHA](input_manifest.json) | 原raw、target、编辑域、保护域、完整透衣体量，均为真实本地文件 |
| [完整局修提示词](prompt_local_edit_zh.txt)／[准备请求](request_prepared.json) | 未提交、未预约执行，必须先过Astra本输入门 |

[白域叠图](qa/edit_domain_overlay.png)、[坐标/前后层次/保护多边形及轴拟合](geometry_and_protection.json)、[实际像素零差检查](target_pixel_verification.json)齐。target SHA256：`a6d23f92bd8eef585881f1c674c2cbafe5c42b7a9a6696437b72430ae0cefa0a`。

模型工具仅暴露参考图、没有独立硬mask参数；这两张mask作为真实参考输入，不能声称服务端会自动保护。后续返回必须经编辑白域取局部，再核保护域与原件RGBA逐像素一致；禁止接受整两人重新采样。

## 同次补项

低位T_H/T_S前段从原件x800–880列的竹色像素分别拟合，外推到x960为y462.533／458.665；旧尾却落在约y470–476。target让正确端点结束于掌下x944、y451.406／452.562，两点原掌alpha均253，故不另加外露尾。四前杆保持原像素；[原低掌错尾放大](qa/raw_low_palm_tail_8x_QA.png)保留。

颈侧减暖和主体外alpha1另列[同raw后处理合同](postprocess_contract.json)，**本轮未应用**，不扩大核心模型白域。原主体外346个alpha1中，保守筛出219个独立小组像素供后续逐点清理，其余127点不直接删除；[候选域](masks/deferred_isolated_alpha1_only.png)排除邻近alpha≥2的3像素范围，禁止全局阈值损伤发丝/细杆AA。

孩子/成人高度比约0.82与施工0.88的差异照实保留：此处不锁尺寸、不缩放孩子，统一注册与CAM20待后核。画布始终1672×941，不自动裁切。原216帧、切点、旧输入/原件/原请求、生产代码、共享留言及ready全部未改。

## 复现与检查

在仓库根目录顺序执行：

```bash
python collab/reviews/cloud_s20_20261018/F000/arm_correction_001/prepare_inputs.py
node collab/reviews/cloud_s20_20261018/F000/arm_correction_001/render_static.cjs
python collab/reviews/cloud_s20_20261018/F000/arm_correction_001/compose_target.py
python collab/reviews/cloud_s20_20261018/F000/arm_correction_001/prepare_request_and_postprocess.py
```

以上只栅格化本地静态SVG与制作显式mask，不调用模型、不渲场景。验收见[作者实看](author_visual_review.json)、[交付验证](verification.json)、[本门SHA清单](SHA256SUMS.txt)。旧门清单逐字节保留，本门单独登记新增文件。

状态：**完整局修输入待Astra审查，未获本轮调用放行。**
