# 090 完整袖腋所有权已修复 · 作者实看通过，待Astra终门

[正常机位完整Canvas](actual_scene/F090_canvas.png)／[完整肩颈袖肘腕](diagnostics/ACTUAL_FULL_NECK_SHOULDERS_SLEEVES_ELBOWS_WRISTS_1to1.png)／[双真握近图](diagnostics/ACTUAL_TRUE_BODY_NECK3_BOTH_GRIPS_1to1.png)。肩背缺面、白花孔、腋下残条、远袖皮肤上缘截断及两颗漏选领片边缘像素均已闭合；正常尺寸实看无当前形体/覆盖阻点。少量衣纹材色接缝留组末统一，终锁由Astra决定。

覆盖代码已修正：连续真实衣片按语义轮廓整块RGBA及原alpha取用，不按花色筛选；真实身体衣面底层保持连续来源。左右完整源臂独立提取，先按已锁向量平移，再按远近合成，不在平移前互减。原整领座/两领片及中央胸面仍取同一片真实旧衣。双握精确位置保留，未缩放/旋转/重配人物，未复制涂抹或补平色。

本轮生图0、交付最终Canvas1、094调用0。实抓2次：首轮核验发现两颗原领片边缘像素漏选，完整原alpha边界补齐后抓最终Canvas；首轮图保留诊断，不另计动作。原件b664008d不变；头颈、腰裤膝胫踝鞋和域外RGBA0变，原地影/箱前景各0diff；内部透明衣孔0，BG/FG重建0diff，真实衣片来源RGBA0diff。[简短来源/保护证明](qa/SHORT_ACTUAL_SOURCE_AND_PROTECTED_PIXEL_PROOF.json)及[来源清单](provenance/SOURCE_AND_COMPLETE_REPAIR_GATE.json)。
