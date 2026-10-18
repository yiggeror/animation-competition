# S24 · 006眼先 / 009起转 / 012过正面，小批交Astra审

唯一采用目录`candidates/`：

| 起帧×停 | 文件 | SHA256 |
|---|---|---|
| 006×3 | [F006_rgba.png](candidates/F006_rgba.png) | `4e363b28a951d7adafcbbe7bb41700086dfa91de0c6fc20ba9bac0641d52af4c` |
| 009×3 | [F009_rgba.png](candidates/F009_rgba.png) | `fa1d4ae70a784d1694d27c674ad28cc9357ced1e6686f9fda8718a60daa65532` |
| 012×3 | [F012_rgba.png](candidates/F012_rgba.png) | `dcbe1e529b03b963f56769e4f0c381cbca5bd2735cdb75d01bbce5f0cd0296c6` |

均为真实图像工具原生1024×1536画稿，经逐态语义区域色门派生。起点为Astra双审锁定的新修母`0485c6fe…eff22`（`6cecf474`），[授权原文](provenance/astra_mother_lock_and_three_state_gate.md)已保全。006实际审后才派009，009首稿转过头被拒，回到合格006重画；009合格后才派012。**旧浅色母与拒收009均未进入任何派生输入。**

实际查看[锁母及三态整图](qa/00_locked_mother_and_three_states.jpg)、[眼/颏颈/耳根近图](qa/01_eyes_jaw_neck_ear_roots.jpg)、[B整层同机位中性底](qa/02_all4_B_neutral_NOT_SCENE.jpg)、[全部三底](qa/03_all4_three_backgrounds.jpg)，另已逐张看原生返回、色门前后及单态B注册。作者接受006眼先右上、头身仍留原位；009完整头颅/颏耳/发根与颈面起转但仍朝左，近耳还在画右；012越过正面略向右，头部近耳/发根换侧，身体近远臂保持原关系。嘴全程闭合，未提前抬颏得意；短尾保持下垂，手肘在画外。F006八处结构边缘搜索最佳平移均为[0,0]，仅辅助“不提前转头”，不冒称全图字节相同。

F009/F012的−14°/+6°是冻结构造意图，**不是生成画稿的实测角度**。请Astra重点审009→012实际转幅、双耳/颏颈接续和后续015目标衔接；当前只开放这三态，不派015。全段采用B=`.70+(590,20)`；alpha≥248实体发顶余量F00092.8、F00691.4、F00985.8、F01282.3场景像素，见[精确注册诊断](qa/registration_and_top_margins.json)。原淡晕alpha保留，没有借色门清边。

原生回图存在区域色偏，已逐张在**同一新修母**的材质域基准上局部校回，未沿上一态累积颜色。三处棕发种子连通域、肤色域、裙黄域分别保留mask/权重；每态取样坐标因真实转头分别定位，012近尾“画左→母稿画右近尾”、远尾反向对应。每态`qa/Fxxx_color_config.json`、`Fxxx_color_validation.json`和`Fxxx_masks/`记录原/后均值与中位数、保护域及像素差。[边界归属审计](qa/semantic_boundary_ownership.json)另记录肤/裙原阈值域13/15/14个边缘交叠，现有脚本从原RGB按裙优先覆盖、未双次叠色；`*_effective_domain.png`明确互斥最终归属，此审计未改候选。全部同语义ROI均值单通道差在±4内，最大为012近尾R+3.8982，接近上限，实际色接续仍请Astra看。保留原局部色阶/腮红；色门相对各自raw的alpha、发部深线/高光保护域和材质域外变化像素均0，不改几何或移动面部。新生状态alpha不冒称与F000相同。

[前15帧中性人物层曝光MP4](qa/S24_first15_neutral_layer_24fps_NOT_SCENE.mp4)：F000×6/006×3/009×3/012×3，24fps、15帧、0.625秒；[实际编码解码接触表](qa/04_neutral15_actual_encoded_decodes_NOT_SCENE.jpg)、[全15帧源/编码核验](qa/neutral15_encoding_validation.json)及五张解码在`qa/neutral_decoded/`。它只合成真实原生画稿到中性底，明确标“DRAWING LAYER ONLY / NOT CANVAS SCENE”，**不是实际Canvas接景或完整60帧成片**；场景/声音/全片渲染0，不登记ready。

本段真实生图**4次成功返回、3张采用候选、1张动作拒收**，工具失败0；加首母共5次。拒收`originals/S24_F009_call_003_REJECTED_overshoot_raw.png`完整保留，不能用于生产。所有raw与工具默认原件逐字节一致；实际完整提示词/参数/输入SHA、原返回字段与提示保留在`requests/`，工具未返回模型版本，不猜型号。[色门脚本](tools/semantic_color.py)、[原件归档及层曝光脚本](tools/finalize_segment.py)可复核。shared生产模块/留言/EDL/声音/ready均未触碰，继续原独立分支交小批审。
