# 完整旧远手孔及AA弧修复 · 零生图 · 原13f有限通过

先看`THREE_PINCHES_BEFORE_AFTER_NORMAL_SIZE.png`（静态正常尺寸）与`ACTUAL_THREE_PINCHES_BEFORE_AFTER_1TO1.png`（实际片同尺前后）。作者及既有云助手实际查看三态完整图、三处夹口和全部13帧解码表：036/042/048旧灰白弧/小环消除，布峰自然接到当前夹指下；041→042、047→048花纹/折面连续，C1承托、完整袖腕掌、真实偶四杆及厚唇T未见新异常。本次夹口HOLD在该修复和原13f范围内解除，未外推后续态/整镜。结论`FINAL_13F_ACTUAL_REVIEW.json`。

本轮**0生图、只渲原13f一次**。`S29_F036_F048_ACTUAL_SCENE_1080p24.mp4`为1920×1080/24fps/静音，036×6→042×6→048×1；SHA **2a27ec9391db4db6d6fe96b1c6bd0788be6089f54a40fb80cd40c2eb60c7f7c4**。实际相机/灯光/曝光/场景代码沿原版，生产源码0改；记录见`ACTUAL_BROWSER_RUN.json`、`FFPROBE.json`、`DECODE_CHECK.json`和`ONE_SCENE_RENDER_REQUEST.json`。

唯一补齐母版SHA **18b478ba2734d3f7f30e254c73284c80bd8d4f4c7e428a4a304a461916c010f9**。完整旧洞+AA域3568点，1038点逐点取已有唯一raw（b8e3ade5…）原RGB，732点真实材料alpha归不透明，域外旧母版RGBA0差。036/042/048均由该母版，后两态复用38f59c2d原网格；当前原始整臂/掌指前景alpha压在布上，不再回贴旧复合孔/旧手mask。手臂M与夹口未重拟，实际偶杆/T及接触ROI外RGBA0差，详`COMPLETE_HOLE_SOURCE_CHECK.json`、逐态来源核对和`FRESH_FINAL_VERIFICATION.json`。

rawalpha0的外侧/指间空气未编造或平铺。剩余小三角具体点见`REMAINING_FINGER_AIR_ACTUAL_SOURCE_TRACE.json`，如048目标(715,653)→原件(728.76912,653.98523)无布源、当前手指alpha0，按真实空气保留。旧洞域内映射原件不透明材质的036647/042539/048594个样点，输出alpha<250缺料0，详`OPAQUE_SOURCE_MATERIAL_COVERAGE_CHECK.json`。旧原件/逐字prompt/完整工具返回仍由2c223b63保全，本轮无新prompt或API。
