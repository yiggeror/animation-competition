# S07 073远左支撑／近右过步 · 交Astra审

唯一取图：[F073_single_native_final_PENDING_ASTRA.png](candidate/F073_single_native_final_PENDING_ASTRA.png)，1672×1080 RGBA，SHA `afc7dcff6593611d0e33b16a7fce9e12967bf1767cacf8336308a51a50af1929`。073–078共6帧；作者与[6.1sol独审](qa/independent_61sol_output_review.json)静态有限PASS，见[深底完整人物](qa/F073_repair02_native_layered_full_dark.png)及[腰／袖根／脚口](qa/F073_repair02_native_connections_dark.png)。不代Astra锁定或整108f镜头验收。

顺链母为本次真实068 `8210a8d56c15a42da4b4daa6c4a4599ce6b2df9b1f5fdab2e1403ec7f9960768`。源快照可逐RGBA重放母068。远左支撑鞋整个图层原位，SHA `1103f923c4e2613dac88e8d1a8534c101103013c4db468af1adcd83426a74e77`；实际鞋底1022native＝774.8743305world。近右完整同鞋相068前移83world、上移63native，鞋底959native＝751.9358026world，实际抬高22.938528world，对约23意图差0.061472。头衣相068(+26.6794858,−5.2495066)world；双完整真臂各+12°／−12°回中位，scale1，玉镯／手指不拆。隐髋沿已过062隐藏proxy及事件增量，不回蓝衫下缘或旧791／744点；不把投影线冒充精确解剖骨长。

073实际2请求／2原件，失败与修后都保全。call01[原件](originals/F073_call01_raw.png) SHA `410209216815230473ebee35340a07fae11b647eb3a6ac9e381c6d85953a8744`把生成鞋画偏，恢复原鞋后近裤口空断22.36native，腰口有367px缺域；[独立未通过记录](qa/independent_61sol_call01_NOT_PASS.json)明确撤回该候选，不能取其`F073_complete_native_layered_PENDING_ACTUAL_REVIEW.png`。

call02按固定真鞋、同一隐藏髋和仅作引导的膝廊，原生重画完整双裤；没有把缺口用代码条桥、像素拉伸或分段变形补住。[call02原件](repair_call02/originals/F073_call02_raw.png) SHA `46a6c90ff08c594dff672f236b1c18e2b4392109af2ec6bf232945f32fdee939`。两原件实际尺寸均1023×1537，整幅统一缩放780/1537＝0.5074821080，左右各补0.4229018canonical px映到520×780，同框贴回(780,280)，无横纵异比缩放。只有真实完整新裤材质进入生产层，源头衣、真双臂和原鞋重组；前近鞋在新裤前，远支撑鞋在其后。

最终排除裤层误采的58px生成鞋材质（其中46px为后跟第二扩边环，另16px暖肤／白底，重合4px），保留第一道真实navy轮廓。四个白鞋边被排出，真实近／远足层均未改；[逐点源映射](qa/call02_shoe_material_exclusion_checks.json)及[mask](masks/call02_generated_shoe_material_excluded_from_pants.png)齐。实际近踝主连接连续，外挑裤口下的细空气带在原生源中同为空，不假造暖肤把它强补成桥。call01诊断、call02取层诊断与最终判定分文件保留。

call02裤料无需RGB校色；均值对固定057为(+0.509,+0.246,−0.322)、对固定062为(+0.262,+0.374,+0.052)，[色门](qa/color_gate_vs_fixed057.json)符合±4。真实头发、肤、蓝衫沿同母材质，不逐态改色。全部真实源层、原生alpha和墨线随独立生产层保存，原始生成鞋／头衣不采用。

两次完整prompt、参数、输入冻结、工具原返回与调用账分别在[call01请求](requests/)和[call02请求](repair_call02/requests/)；host原PNG、返回base64和归档PNG已逐字节核同。初次输入的`PREPARED_NOT_CALLED`是历史，不是当前状态。重放顺序：`compose_native.py`保留未通过call01 → `compose_repair02.py`得到最终修后图，再复制到唯一final。冻结后的两个`prepare*.py`不重跑。源图层与最终PNG的独立隔离重放、057／062／068／073真实曝光见[小段交审总入口](../segment_057_078_delivery/README.md)。079未开。
