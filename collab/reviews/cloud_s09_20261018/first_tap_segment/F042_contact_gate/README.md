S09 F042第一触掌已完成作者实看与云6.1sol限定PASS，现交Astra审。不是整镜ready；044/048未启动。前态唯一使用Astra已锁a1d7f27的037（68ce16f1…695c9）。

唯一取图：[`connection_call02/candidate/F042_complete_joint_pixels_v2_PENDING.png`](connection_call02/candidate/F042_complete_joint_pixels_v2_PENDING.png)，SHA `c909ea491e345021299dd7deada41b2a1748b6c12fc2c743e58242195d8a0270`。

实际曝光：[`exposure/S09_F037x5_F042x2_actual_layer_24fps_PENDING.mp4`](exposure/S09_F037x5_F042x2_actual_layer_24fps_PENDING.mp4)，7帧/24fps、无音频、无补间，仅隔离人物PNG层。SHA `10ddf0abc8dba338207410db0489ed4fea0e813fc56aac5dee166f9518ec53e6`。全部7帧已解码核037×5→042×2，最大RGB MAE1.28713；实际0/4/5/6接触表在`exposure/actual_decoded_0_4_5_6_contact_sheet.png`。没有进行全镜、全片或Blender渲染。

原握手与完整手筒从037同步下91raw（031下59raw），保轴线/长度/直径/握持；左托掌固定，尾盖落到掌垫。实际原生近臂经单一整臂刚体配准后，第二次真实局修去掉袖口重复弧、接顺腕下缘并清旧臂残线；最终两处取用边界由同一个原生输出补全，未追加请求、未拆伸手臂。真实握持手指/掌与整筒、外近褶袖、头眼及稳定托掌保持源像素；近袖内缘和近端腕人工提取边为接缝修绘，不冒充原像素完全冻结。远整圆袖保持底层，随前景近臂形成合理遮挡。

本态2次请求/2份原件，总S09累计17请求/16原件。首次返回整图有手筒/托掌偏位，禁止整图使用，仅选真实整近臂；04/08度试配、06未接缝版、v1均标未通过并保留。两次完整prompt/参数/输入SHA/raw_return与原PNG在`requests/`、`originals/`及`connection_call02/requests/`、`originals/`。两份PNG均与完整返回base64及工具原路径逐字节一致。未重送历史037被拦请求。

实际独审记录：[`independent_61sol/connection_call02_v2_c909_static_and_exposure_PASS.json`](independent_61sol/connection_call02_v2_c909_static_and_exposure_PASS.json)。作者与独审均看实际PNG/接缝对照/实际解码接触表；没有把ffprobe、文件存在或单静帧替代整镜双击因果验收。极放大1px墨边/AA阶差当前显示尺寸未构成断腕、双袖或双轮廓。数值代理不作为解剖骨长实测。

重放/证据：`zero_call_whole_arm_trial.py`只原像素整臂刚体与背景取用，`connection_call02/recompose.py`为初取，最终用`connection_call02/refine_adoption_v2.py`，`build_exposure.py`重建并逐帧解码7f。原请求操作mask保留原SHA，最终语义取用mask、来源、接缝范围与0域外变化见`connection_call02/qa/refined_adoption_checks.json`。准备脚本有STARTED防覆盖门，不应在已执行目录重新准备/重复请求。

S07单态髋门已独立推77ab772，不与此包互等；本分支只写独占review目录，无实现/共享文档/ready/EDL/音轨修改。
