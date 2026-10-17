# S29 奶奶六态整镜候选，可由 Opus 一次接景

接入入口：`complete6_work/COPY_MAP.json`。复制其18张三图与 `assets/flips/g29_wrap.flip.json` 至所列仓库路径；本次只发布在collab，不改生产。母版仍是g29_wrap，帧名g29_cloth_close_k01–k06。288帧manifest及协调独立六态RGB/alpha核验通过。

完整动作：原半包→深收口→送边→双手压平→松持落定，末态全闭短眨。实际生成T/P/R/B各一次，4次结束，无重抽。已实际双人看原件/正确alpha手、脸、凳；独立H名义均≤1.41px。原件都保留在 `complete6_work/inputs/`；本包将作者本机软链接物化为普通PNG，故无需任何外部本机路径。T/P/R/B另见 `complete6_actual/raw/`。复现从complete6_work运行现有tools/prep_flip.py inputs/*.png，然后tools/flip_manifest.py g29_wrap 288。

可见新画只覆盖F0–239；F240–287表内保持仅作接口回退，必须沿用旧靠灯段，不显示本卡冒充新画。小满原8.1–8.42秒AB不改。

布声按实图建议F24内收、F36送边、F39压平、F65松持，详见 `complete6_work/reports/exposure_and_cues.json`。请实际重排/重建后给文件与哈希，旧母带结论不得沿用。

保留条件：T实际手路较大；凳纹/裤线重画，B脚NCC最低0.561，不能单凭小H说像素冻结；R局部脸/镜圈略移；末态最长开眼44帧。以上须看实际接景换帧和原速节奏，不称成片通过。详细作者说明在complete6_work/README.md。S30停止生成；S31另交完整有限状态包。
