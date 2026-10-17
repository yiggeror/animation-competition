# 透明关键帧预处理实测

本次两张原件是RGBA透明PNG，不是旧版灰底RGB。现行prep_flip.py无条件调用cutout.py，后者先convert RGB，会丢原alpha再按颜色重新分割。

已在隔离路径实际跑当前cutout.py处理v2（922×1706，43ef437c…56e3），检出的背景为黑色(0,0,0)，不是浅灰。原alpha<16却在输出alpha>128的像素有10116个；原alpha>128却被削到<16有1129个。实看 original_left_recut_right_stool.png：右边重抠结果将凳座下、腿边和鞋底隐藏红黄碎像素变成可见杂边，左边原件正确alpha合成没有这些杂边。这是实际预处理破坏，不是原生RGBA查看器问题。

最小候选prep_flip_preserve_alpha.patch：检测有实际透明度的A通道；已有RGBA时直接复制原件，再运行现有card_maps/card_soft；不透明旧输入继续原cutout路径。没有应用仓库。用修后完整pipeline对同一个v2实际运行，固有色字节与原件一致，三图尺寸都是922×1706，三图alpha逐像素等于原件；见corrected_result.json。若后续统一分辨率，应在统一后的保真alpha图上生成maps，三者同画幅。本补丁不修生成姿势，也不代表整镜打光通过。

原件/脚本/结果SHA见result.json；修后脚本及实际三张输出在corrected_pipeline/。原件未覆盖。数字证明alpha变化范围，问题判断同时依据实际合成图。命令记录：python3 -I tools/cutout.py <v2原件> /tmp/laidian-s18-cutout-v2.png 14 0,0,922,1706；修后在隔离cwd运行python3 -I tools/prep_flip.py <同一v2原件>。没有新生图。
