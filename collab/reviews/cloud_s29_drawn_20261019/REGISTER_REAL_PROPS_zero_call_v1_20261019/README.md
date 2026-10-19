# S29 零生图统一注册＋原偶接层 · 单张候选待 Astra

先看 [正式机位1920×1080](scene/S29_F000_FORMAL_CAMERA_REAL_ORIGINAL_PROPS.png)、[近掌／原neck3实际近图](contacts/C1_NEAR_PALM_ORIGINAL_NECK3_ACTUAL_FORMAL_CROP.png)、[远夹布／尾羽实际近图](contacts/C2_FAR_PINCH_CLOTH_OVER_TAIL_ACTUAL_FORMAL_CROP.png)。两近图均从这一张正式图直接裁取，RGBA逐像素相等；不是另拼的接触图。**本阶段0生图、0后态。**

保留已通过整母原件 `b69923f3…58cb60ecb`。完整人物、手掌、布外沿、双腿、凳、鞋在原生域内保原RGBA；只清生成偶／杆残像并补布底，显式mask及重放脚本随包。补布用同原母未遮挡蓝棉布真实纹样，排除全部人体候选；蓝底归一以收掉补块接缝。隐藏布纹是有限修复，不能声称恢复了原本不存在的像素。

整母＋道具只用一个等比映射：`s=1.0026666666666666, tx=277.33333333333337, ty=-6`。当前实际t=0机位、背景、幕与照明沿用原生产；相比旧母注册仅整卡下移30输出px，保住新母较高的发顶，不单拉头、臂或掌。未继承旧收布warp、AB转头或旧时表。

真实两偶调用原 `makeCrane`／`makeTurtle`，保持各自所有部件形状与原rig。共同膝面投影 `.55 px/mm × −.33 px/mm`（共同0.6短缩视觉参考，非3D反解）；鹤整体定位，使真实 `neck3[10,0]` 段内点到新挑近掌扶点 `[536,750]`，不是将其冒称铆钉。远布夹点 `[845,744]`。`pointOn`之后仅镜像一次。

四根直杆从真实鹤 `body[-75,6]`／`neck3[10,0]`、龟 `shell[0,40]`／`head[20,0]` 起线；自由杆尾留膝布内。层序：原双膝→补布底→四杆→完整原两偶→原抬起布沿→原近掌。原生成偶／四杆不采用。旧代码小满持龟层按导演“不交签”排除，未重画小满。

已实看正式全图及两近图，既有6.1sol只读复看确认原颈入指下、远布压尾及清理问题收住；**仍待Astra真实接层主审锁母**，不泛称掌内所有五指拓扑或完整后段已过。代码、原始来源与保护实证见 `sources/`、`qa/FINAL_ACTUAL_VERIFICATION.json`。

实际生产读取源 `8065837662b3c1252d82a0bf75e9837ac12523dd`，六个相关文件逐字节核同并只读留快照。浏览器仅拦截返回附加 `export {shot}` 来读原私有shot，磁盘生产源码0修改。两次资源记录无失败／页面异常；非200见原日志。无整镜渲染、共享文档或Opus留言变更。

重放（现有Python+Pillow+NumPy+SciPy+OpenCV、Chromium+Playwright）：先 `OPENBLAS_NUM_THREADS=2 python prepare_layers.py`，再 `node render_registration.cjs props`、`python compose_native.py`、`node render_registration.cjs scene`；工作目录为本目录或传完整脚本路径。OpenCV本轮临时装在 `/tmp/s29-image-tools`，不进入生产依赖。重放只读原件和生产原偶，不读取最终图作为计算输入。
