# S29 单次首母原件 · 待 Astra 实审

沿用 `cloud/s29-drawn-reference-20261019`；Astra 已通过输入门 `2686cb049dfd466de694dad6a4e728bfd48f65bb`，本次只执行已批准的一次首母请求。**1次请求、1张返回原件、0重试、0后态。**

先看 [未改原件](originals/S29_FIRST_MOTHER_call01_RAW.png)，再看 [灰底透明度实证](qa/FULL_RAW_ON_GRAY_ALPHA_DIAGNOSTIC.png)、[近右裸腕／neck3](qa/C1_NEAR_BARE_HAND_NECK3_ACTUAL_CROP_ON_GRAY.png) 和 [远左镯腕／布沿](qa/C2_FAR_BANGLE_CLOTH_LIP_ACTUAL_CROP_ON_GRAY.png)。原件 1024×1536 RGBA，SHA256 `b69923f306d14ee5f1bfe83110998f8f9891ee8f5263e3e7edf257d58cb60ecb`；与工具原宿主 PNG、完整工具返回内 data URL 解码字节完全一致。

已实际看全图和两处原像素裁图：双臂连续，近右裸腕、远左单镯；布为自然软棉布，远手可见拇指／手指夹抬布沿、布面承托两偶。近手位置到鹤颈接点，但真实原偶 neck3 两侧的拇指与对指夹扶未充分显露，**不能仅凭此图称真实夹扶已通过**。生成的两偶和四杆只是上下文，原生产皮偶、四杆后续仍须独立接层复核。统一接景尚未执行，不以本图冒充接景验收；不开后态。

透明度实际存在：719795个全透明像素，三个背景采样均为0。查看原图时可能看见透明区内隐藏RGB色雾；灰底合成已实际检查，色雾不出现在有效背景。主体 alpha 多为252–254，原件未归一化或修补。裁图／灰底图仅作实看诊断，原件保持原始字节。

[实际完整参数](requests/arguments_FINAL_EXACT.json)、[完整提示词](requests/prompt_FINAL_EXACT.txt)、[完整工具原返回](requests/tool_return_FULL_ORIGINAL.json)、[批准与次数约束](requests/AUTHORIZATION.json)、[实际五输入完整SHA](requests/ACTUAL_INPUTS_SHA256.json) 均已归档。`frozen_inputs/` 为已批准五输入的逐字节副本；工具实际读取这些路径，未增补参考。完整工具返回含原始 data URL，不是重建元数据。

[实看审查与局限](qa/ROOT_ACTUAL_RAW_REVIEW.json)、[原件来源与一致性](originals/RAW_METADATA.json)、[透明度实际统计](qa/ALPHA_FACTS.json) 随包。仅此独占目录新增文件；原准备包 README 中“生图0次”是输入门阶段历史记录，本目录记录这次实际执行。无生产文件、共享文档、Opus留言或其他镜头改动。
