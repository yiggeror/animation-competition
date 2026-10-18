# F057 单次局修实图 · 步幅和远腕仍未通过

**新增零调用提案：[完整腿链刚性内收／真实鞋底支撑／远臂可达范围](zero_call_pose_proposal/README.md)**。新调用0，腿部预摆约64横距、鞋底774.87；整臂原长度下腕仅到约947/594且受衣遮挡，仍NOT_READY，不开接缝生成。本页以下保留call02实图历史，原件未覆盖。

本轮原生局修 **1次／1原件**，S07本作者累计 **2次／2原件／0采用**；其余10态生成0，在途0。Astra已通过七态摆臂v2，本次只执行获批的057完整腿链及远左整臂修复，没有扩后态。

先看 [实图与目标对照](qa/call02_actual_vs_targets.png)、[原始返回局部坐标](qa/call02_native_coordinate_inspection.png) 和 [实量记录](qa/call02_actual_review.json)。真实返回朝右身份、近右裸腕／远左玉镯和裤腿连通可读，但踝横距约 **91±6世界px，目标64**，近踝约(958,748)，比目标(929,758)前29；远左腕约 **(983,588)，目标约(942,623)**，仍前41／高35。双鞋底约769／771，目标775，未宣称落地门通过。作者与[只读云端6.1sol实看复核](qa/cloud_61sol_call02_actual_review.md)结论一致：**057未通过，不能由此扩后10态**。

## 已补齐实际G037尺度源

源固定提交 `9ee7689d8ff56ab6c366a7f6d087197f0c8d6377`，原路径 `collab/reviews/20261018_1624_s07_g037_reference/`，原样复制于 [sources/G037/](sources/G037/)。真实站姿PNG `F037_grandma_rgba.png` SHA256为 `4ebf2dc030fc8afd1cc53fb0269b31b0e4b7c4c416019ec47c3a045341ac4f8a`，1024×1536，注册s=.2734375、t=(730,375)。已实际看图；头顶到下颏约253±5源px，即69.18±1.37世界px。旧75.1只属施工头尺，已撤作实量依据。G037左向图只用于尺寸核验，**从未镜像，也未作为局修图像输入**。衣下髋、肩关节及真实骨长不可从衣面精确反推，不作实测骨点宣称。[量核与限制](reference/G037_actual_scale_check.json)、[头尺度同尺实图](qa/G037_F057_actual_uniform_head_scale.png)。

## 本次执行范围与实际输出

唯一画稿来源仍是首call01原件 `2aa44731…bcb9f`。只在原1672×941下方加139透明行至1672×1080，原像素不缩放；完整腿和远左整臂原像素作刚性预摆，并覆盖完整链重构域。预摆图仅是施工输入，不是采用画稿。头颈、蓝花衣形及近右整臂以黑域逐RGBA锁住。远臂目标从真实袖口接出，避免从腰部穿衣生成皮肤；近／远踝目标(929,758)／(865,758)，地面775。[全部预摆坐标与来源](reference/preparation.json)。髋允许小幅自然变化，未以移鞋或分段缩放冒充缩步。

实际输出 [F057_call02_raw.png](originals/F057_call02_raw.png)，1560×1008 RGBA，SHA256 `549cd22c715a1724d6546ede9c2b084173d5592d4dde1ac884707d0490841449`；已核工具原始返回base64、宿主生成文件与归档PNG逐字节同。返回有效透明度并已[叠浅底实看](qa/call02_raw_alpha_on_light.png)。因工具改变画布尺寸，仅作整张返回等比1.07179487配准，再用原源恢复黑域；没有对头、手臂、腿或鞋分别缩放、形变。候选 [locked_domains_NOT_PASSED](candidates/F057_call02_locked_domains_NOT_PASSED.png) 及 [世界坐标图](candidates/F057_call02_world_NOT_PASSED.png) 均明确未通过。重放核验mask外变化0、保护头身／近右整臂变化0。

## 可重放与审查门

[实际参数](requests/F057_call02_arguments.json)、[完整提示词](requests/F057_call02_prompt.txt)、[完整工具返回](requests/F057_call02_raw_return.json)、[实际输入哈希](requests/F057_call02_inputs.json)齐全；原件、输入图、mask不覆盖。[review_call02.py](review_call02.py)核原件／返回字节、prompt一致性和输入哈希，重放同尺配准及锁域并输出实际偏差。`requests/*PREPARED_NOT_EXECUTED*`是早期75.1／83透明行草案，**从未调用**，不要误当call02参数；旧预摆字节可查提交 `1b7c3a0b0a9ad7d07f16ba5e96093d10508692ec`。

先交Astra看本次真实源尺度和局修偏差，再决定是否另做必要局修。不从未过态扩后10张，不重复整人数字提示重绘。本轮无整镜渲染、Blender或新服务调用。
