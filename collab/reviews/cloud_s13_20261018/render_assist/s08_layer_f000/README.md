# S08 F000新前景层次 · 实际单帧复验

固定`23ced01306239a15a55f42a8d46e23fe375b9c63`，入口`collab/reviews/20261018_1631_s08_layer_diag/s08_f000_layer_scene.js`。已通过仓库原`snap.cjs`和系统Chromium真实渲染t0，1920×1080；[新实际PNG](S08_F000_layer_actual_1920x1080.png)、[此前实际PNG](S08_F000_original_actual_1920x1080.png)、[肘/前唇实际对照](elbows_old_new_actual.jpg)、[双手道具/灯实际对照](hands_lamp_old_new_actual.jpg)。未生图或修改任何源模块/人物/桌/灯/光/机位。

实际观察：两肘下缘现在完整画在原前唇前，不再被前沿截平；近肘仍靠桌左角，读为靠近或略越前唇，没有把它解释成深放桌面。前唇在肘两侧连续，下躯干仍在桌后；双手、火柴/盒、灯的位置与遮挡不变。未新增接触阴影或移动接触点，最终空间接触由Astra裁定。

[像素对照](actual_comparison.json)：只变化1272像素，包络`[761,978,1089,998]`，全部位于两肘ROI，ROI之外变化0。母图互斥两层alpha无重叠，按选区还原与c803原RGBA逐字节相同。新PNG SHA `6504e01d6f3bb2749ddc6dc65bf8edd5a1f7cb8e44d415a4615ce3f7cd103380`；旧实帧SHA `9b63b3605aa59b8383e87f0322bceee1078e4486cd27e71d9c067b79a44d9ccd`，来自已交b1fa2bac。

[短运行日志](render.log)与[源/原命令](source_and_command.json)齐全。本包只验F000实际层次，不代完整S08、后态动作或声音通过，未改EDL/音频/ready。S13当前另处于退回待修色状态，本辅助结果不改变该状态。
