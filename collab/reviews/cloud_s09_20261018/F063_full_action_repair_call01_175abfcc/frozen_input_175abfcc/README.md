# S09 F063 完整动作带形体修输入门：五图，0新调用

按Astra最新主／独审方向，放弃拼68cde/3ef32eda当前试件。此次只准备一次完整局修输入，**尚未冻结、尚未调用；没有F069输入或画稿**。旧044高腕整握组、当前063细筒与过远掌位均不作姿势锁。

先看 [A完整target](reference/A_F063_PREPARED_NOT_CALLED_1280x1536.png)、[B完整白域](reference/B_F063_PREPARED_NOT_CALLED_1280x1536.png)、[C同target软链／接触](reference/C_F063_PREPARED_NOT_CALLED_1280x1536.png)、[D044真实筒全轴／截面](reference/D_F063_PREPARED_NOT_CALLED_1280x1536.png)、[E身份／布料／去腕的局部指筒接触](reference/E_F063_PREPARED_NOT_CALLED_1280x1536.png)。五张均1280×1536；[灰底全图](qa/full_target_gray_NOT_ART.png)／[深底完整动作带2倍](qa/full_action_band_dark_NOT_ART_2x.png)。技术色块、关节和筒是明确NOT_ART参考，不能当绘图交片。

## 单次重建范围与保护

完整重建胸腹黄裙背层、近袖根→低肘→前臂→自然腕→新握手＋正确粗细整筒，以及远袖上臂／低肘／前臂／腕掌的迎接带。远臂在躯干后、近臂在前，两前臂本体不交叉；远上臂起点与近前臂有投影遮挡，按层次藏后，不能画成从近前臂长出。头颈领、近整ruffle、稳定裙逐实际护mask保留（包含源领边邻接的真布），A原生RGBA0变化，白域护域交0；不把透明像素作保护。

冻结T=(858.338855,636.929471)、L=(1227.000238,562.998526)，轴长376.001330native不变。044真实可见材料法向跨度：尾帽80.066、红筒68.085、灯帽124.023native，边归属约±3；手工完整尾径83±4另列，均为2D投影尺度。D没有旧手／腕，遮挡缺料明确UNKNOWN；A用完整正确粗筒技术体量补全结构，不非等比拉旧细筒，不伪造隐藏旧道具RGB。E仅小块真实指筒接触，旧腕和整臂已排除，不竞争新握姿。

近E(790,730)、技术半宽36→下缘766，nearW(1000,658)是可调整的姿态代理；前臂由左下进入新握，保低肘与裙边空气。袖口入口不是骨关节，不能把袖口到肘的106.4投影当完整上臂骨长，或与222前臂直接比较。本包不认证新骨长，成图仍要审真实体量、腕折和近臂裙接。

## 远掌真实轮廓净空与可达性

当前过远掌位已撤销。新迎掌仅作软guide，用5077源完整掌指（含短腕入口）整体相似变换至原迎接带，整只远臂腕掌都允许重画；手腕源截口在完整白域内，未硬保旧腕。

[真实灯缘→完整掌轮廓灰底4倍](qa/REAL_prop_to_whole_palm_clearance_gray_4x.png)／[深底](qa/REAL_prop_to_whole_palm_clearance_dark_4x.png)。量的是实际044道具与实际源掌材质轮廓：α128=15.0native（最近掌1217,639／灯1217,624）、α16≈13.342、α1≈10.050，均无接触；不把所有可见AA统称15。真实掌到近技术握／臂另有α128约28.018像素，未提前碰握。

[063→首次接触六步研究](qa/063_to_contact_SIX_STEP_PROXY_REACH_STUDY_ONLY_gray.png)／[完整数据](geometry/continuous_reach_and_real_reference_checks.json)：完整掌整体向上15，α128间隙15/12/9/6/3/0；远低肘连续从(1005,810)至(1022.160848,803.652719)，保持两段**代理**长度125.9603／160.3110，头裙交0。末步是前指尖首先碰灯圈、α128交3像素，弱AA更早相遇，**只说明首次触及可达，不是069掌垫托稳、闭握或真实曝光通过**。未制作F069输入，实际新063及将来069仍须另审。

## 来源、全文与复核

[完整388词草稿](requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt)，SHA `afc74d1dc1a2ce069070000a1b60766f46a680d6a4db33b2736606c39b45a133`；[五图精确预备参数](requests/arguments_PREPARED_NOT_CALLED.json)。新原生裁切为(550,0,1320,924)=770×924，整体128/77至1280×1536，唯一逆配准77/128+[550,0]，不沿旧700×670裁切或旧共同M去配新图。源掌的小组变换只是输入软guide，不是将来生产配准。

[root来源快照](sources/snapshot_manifest.json)与[真实道具来源](real_prop_reference_61sol/sources/snapshot_manifest.json)保留原提交／原坐标／原RGBA；F026碎衣、旧高腕、当前细筒没有混入target。当前输入无新原始返回，因为没有调用；以前生成的原件与完整prompt/返回保留原调用包，本包只复用其明示来源掌材质。

root和6.1sol分别实看五图、全文、完整动作带与接触研究：[核心有限审](qa/61sol_full_action_gate_review.json)／[完整五图与全文有限审](qa/61sol_full_five_input_review.json)／[root有限审](qa/root_full_input_actual_review.json)。结论仅“输入准备可交Astra冻结”，不是成态或调用许可。`python verify_input_gate.py`只读核12项真实来源git字节、护域／真实净空，并在临时目录从sources重建全部五输入、原生参考／层／mask与几何。
