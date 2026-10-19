# S20同视角详图、三条三时点与F000输入：零生成小门

Astra已冻结动作协议：F000–057补真递龟，小满R头/L壳不换绑，F132–143先并鹤签，F144保原切。本次只修详图/接触过程并准备首F000输入，尚未代Astra宣布此小门通过；新生图与角色输出均0。

[当前K01](../../reference/S20_K01_F020_handoff.png)、[当前K02](../../reference/S20_K02_F084_crossed_rods.png)、[当前K03](../../reference/S20_K03_F156_laugh_bundle.png)。K02详情直接裁取主图`[355,530,555,695]`，K03为`[600,680,800,810]`，只正向等比放大4倍，不重画手、不镜像、不转角。最终主图对应RGBA与保留原生裁片逐像素相同，[实际裁切记录](same_view_details.json)。K02保留R/T_H上、L/T_S下；K03保留橙C_N上、绿C_B下。两C杆在掌中的轴线接入各自接触区，拇指保持两杆夹持而不是一个公共圆圈；四个接触带各有独立的拇指侧及对侧指腹侧标记，掌内轴用窄色虚线剖示。

三条“原握→接握→放握”均已放回原三页底部：

| 原页/转移 | 原握 | 接握（供手仍闭合） | 放握（受手维持） |
|---|---|---|---|
| K01 龟双签 | F008：G.R持T_H+T_S，小满未碰 | F020：X.R头/X.L壳已夹牢，G.R仍支持 | F032：X.R/X.L维持，G.R张开撤离；鹤两签始终G.L支持 |
| K02 接回C_B | F036：G.L持C_N+C_B，G.R尚未接 | F042：G.R已夹C_B，G.L仍夹两签 | F047：G.R保持C_B；G.L仅撤C_B接触，C_N仍在L |
| K03 并入C_N | F132：G.L持C_N，G.R持C_B | F138：G.R已夹两签，G.L仍夹C_N | F143：G.R维持双签，G.L才张开撤离，随后扶腹 |

[三时点状态原始数据](three_time_transfers.json)与[校验结果](verification.json)检查每根转移杆在原握/共同接握/放握三态都有人支持；供手不在共同态前松开。底部只是局部手端接触时序小示意，不添加人物曝光或新机位。单独裁片：[龟交接](../../reference/details/K01_three_time_strip.png)、[C_B](../../reference/details/K02_three_time_strip.png)、[C_N](../../reference/details/K03_three_time_strip.png)。

[首F000唯一实际输入、完整提示词与5输入清单](../../F000/README.md)已独立准备。F000为奶奶独立持四杆、小满两手张开零接触，姿态手臂/掌位与F020共同接握中态不同；F020不在准备请求里，工具未调用。

原`S20_216f_beats.csv`、`S20_216f_frame_phase_map.csv`、`S20_reference_plan.json`与58a44a4原字节一致，216帧、F132翻肚和F144原切均保持。旧JSON的“未冻结”是首交历史状态，本次动作协议冻结由[明确指示及基线](protocol_and_baseline.json)与本页更新说明。K01已接受的左侧主体/手杆图与首交逐像素相同，仅新增所要求底部时序；K02补接触标记，K03仅修手中双杆夹持接触，完整身体关节施工尺不变。

复现当前小门图，全部只做静态参考输出：

```bash
python collab/reviews/cloud_s20_20261018/tools/build_references.py
python collab/reviews/cloud_s20_20261018/tools/build_F000_input.py
node collab/reviews/cloud_s20_20261018/tools/render_references.cjs --with-f000
python collab/reviews/cloud_s20_20261018/tools/derive_same_view_details.py
node collab/reviews/cloud_s20_20261018/tools/render_references.cjs --with-f000
python collab/reviews/cloud_s20_20261018/tools/prepare_F000_request.py
python collab/reviews/cloud_s20_20261018/tools/verify_gate.py
```

`prepare_F000_request.py`只写准备请求，不调用模型。旧独立重画的错误详图可在58a44a4历史提交查到；本次记录保存主图原生裁片与当前SHA，不以旧错序图作输入。共享实现/留言/EDL/audio/ready及生产主分支均未改。
