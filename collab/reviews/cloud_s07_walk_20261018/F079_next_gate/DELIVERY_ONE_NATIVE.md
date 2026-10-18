F079唯一原生回图，供Astra单张技术审；当前作者未通过，不能视为锁定态。

- 固定输入：68f47899c06cb95b6a5188784951d864cc424293，四PNG与完整prompt逐字节未改。
- 本次1请求/1原图；native1024x1536，按同一画幅整体均匀映射为520x780，原裁窗900,280,1420,1060。未拆肢缩放/改姿。
- 原始PNG：`originals/F079_call01_RAW.png`，SHA f10e92b0cc1155dad3746d00e45559f2fd2598a171ec832d9d858478a6cb274e。完整工具base64与host/archive逐字节一致，host路径及完整请求均保留。
- 源层试件：`candidate/F079_one_native_source_layered_TRIAL_PENDING_ASTRA.png`，SHA23917123ffe8f0a06fea3a0dbed4ae25fbc85872d2bba21dadaa70cebdf4df4b。
- 实看：`qa/F079_one_native_layered_crop_gray_TRIAL.png`、dark对应图；`qa/F079_one_native_actual_connections_gray_TRIAL.png`；`qa/F073_F079_one_native_actual_comparison_gray.png`。

原生完整腰臀/双裤腿抽取自这唯一原图；返回的328px蓝衣/肤/白鞋材料从裤层排除，未画新裤或接桥。真实头衣/整臂/双鞋踝五层沿冻结预摆，production拷贝SHA全部一致，六层重放试件零RGBA差。远左完整鞋仍与锁073逐字节同，近右原鞋完整前落，双实际sole1022。原生navy均值对062(+1.45449,+1.26125,-0.66285)，每通道≤4；未RGB修正。

腰衣下原生navy连续，两裤口与真实源踝未见大透空；但近右腿仍明显斜前大腿→折膝→回折小腿，接近旧073轮廓，自然前落伸展和腰臀承重尚未过作者审。详见`qa/root_actual_one_native_review.json`。不能凭新生成鞋自洽，亦不把软髋膝proxy当硬实骨长。

`compose_one_native_trial.py`仅重放真实源/原生材料；不调用图像工具，保留自然AA，不冻结alpha0空域。没有补调、后态或曝光；S09接回由Astra专员负责，本轮未触碰。
