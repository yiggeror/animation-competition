# S07 F084 call02：一张真实原图与完整裤体试稿，待 Astra

唯一按 `e92f6721da3d31c438b6d4682a51be262a5bfc1a` 已审四输入及原两段英文执行一次。调用前核为零在途、纠正输入零原件；本次一请求一原件，F084 累计两请求两原件。无追加调用，090未开。

原件：`originals/F084_call02_RAW.png`，1024×1536，SHA `543bf9fee8f3b96c284660abee6a298bea9c14b6b0b98eedc0a35b68e197ef70`。完整工具返回、含base64的原始结果、宿主来源、冻结四图及prompt/args均保全。

待审候选：`candidate/F084_call02_complete_volume_PENDING_ASTRA.png`，1672×1080，SHA `21acf20424d94477191dbc6fd012fe61426d509ec55dbc48037bb97b2c89f6ae`。仅整幅逆变换65/128加原点(1000,280)，无全身fit、分腿缩放、挪鞋、画桥或代码人体。

先实看并核衣摆、两完整臂及两只真鞋的已知注册，再提取真实原图的两片完整裤料大体积（合63724native材料像素），不重画形体或校色。六层由后至前：真远鞋→新原生完整裤体→真远臂→真头衣→真近臂→真近鞋。五个原层逐字节不变，后鞋完整底层自然被新近胫覆盖5021个alpha128像素，无鞋形割腿。原RGB/alpha及实AA保留。

实看入口：`qa/F084_call02_source_layered_crop_gray_TRIAL.png`、`dark_TRIAL.png`，腰臀/双裤口/袖根近图 `qa/F084_call02_actual_connections_gray_TRIAL.png`、`dark_TRIAL.png`。已知逆变换原图与A的对照也在qa。两前臂/衣身可见材料轮廓95百分位偏差分别1/2/1native；近鞋白底材料边界95百分位1、可见远鞋2native以内，不把隐藏远层alpha当注册标准。

本候选的完整腰臀与两条真绘裤腿连续，近右腿在前接低支撑鞋，远左腿向画右前过、屈膝后小腿回接抬鞋。远膝比软K引导约高50native、屈幅更明显；软点不是实测骨点，此项留Astra动作幅度/真实体量审。裤料语义均色相对锁057/062各通道均在±4，RGB修正0；均色通过不代真实体量和连续曝光通过。当前只交单态，未锁定、无曝光/整镜验收。

`compose_single_native_trial.py`可用原件和冻结输入隔离重放。提取mask/排除非裤材质mask、已知注册材料核、来源SHA及有限实看审查均在包内。
