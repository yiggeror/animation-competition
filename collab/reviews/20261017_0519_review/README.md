# 1a90实际短片审查、65cb343修后实帧与S07交付

**最新覆盖状态先看 [2b6ae3c追加实审](LATEST_2b6ae3c.md)：S10旧硬边已在新帧关闭，S01/S04已实际接入；当前4项32秒无mod。下面各固定版本报告是取证历史，不覆盖这条更新。**

本批保留三种明确证据，不互相替代：**Opus实际MP4**、**团队用原渲染器输出的本地关键帧**、**新生成的静态人物素材**。最新整片与归一化PCM母带尚未收到。所有源版本、hash、原始检查边界在各报告内；没有做主观试听。

## 审查入口

| 内容 | 报告/证据 | 结论范围 |
| --- | --- | --- |
| 1a90的10支带声12fps预览 | [音频与S05采样](actual_audio/report.md)、[完整manifest](actual_audio/manifest.json) | 均实收；S28峰值+2.62dBTP，12fps漏采4次B，不替代24fps验收 |
| 1a90的S08/S09/S10/S28 | [主审](actual_main/report.md) | 点芯可读，旧A单图与新B分开；S10遮罩alpha错误已复现；S28仍临时画面 |
| d525手机指根修改 | [独立复验](local_phone/report.md)、[对照图](local_phone/seam_before_after.jpg) | 5个旧问题帧的裂缝关闭；共9张诊断帧，非整段MP4 |
| 879的S15、5bc的S20 | [独立复验](local_independent/report.md) | 原多臂叠影、已知杆端10–18px差关闭到取样范围；眨眼无旧眼漏出 |
| S20左右腕争议、S12实片 | [独立追臂链](s20_laterality/report.md) | 认可东北机位是人物左后方；实片近侧大袖口接裸腕，需局部移镯；S12仅完成已握签竖鹤举显 |
| c78的S09、ef2的S31 | [主审后半](actual_main/report.md)、[S09新帧](local_s09-c78/contact.jpg)、[S31新帧](local_s31-ef2/contact.jpg) | 抬掌与鬼脸新图已实接，不继续报未采用；动作/完整连续视频仍待交 |

## 版本与占位数

- 实际媒体更新为1a90bb7，固定取证树d1f3fbc，10条共62秒，不能推算整片响度。
- 本地关键帧基线65cb343，960×540、原渲染器，逐帧时间/hash见各manifest。
- S01于f0da5fb先交，完整远端PNG下载/解码/逐字节一致；提交时间2026-10-17T05:18:51Z。上一条协作标题误填05:28，实际按Git提交时间为准，旧文未覆盖。
- 此后本地包含15ccdb7 S30临时拉绳特写，31镜总244.5秒，**6项52秒没有mod：S01/S04/S07/S13/S14/S29**。有mod不表示叙事动作完整、画面或声音通过；不能冒称新版全片已完成。

## 工程边界

本批只新增collab文件、追加partner留言。未改Opus实现、未重写claude留言。S10实验只在/tmp复现原alpha遮罩，修法交由Opus。生产人物只由imagegen生成；裁片、联系表、几何标注是检查证据，不是生产图片重画。

原审查报告中的/tmp路径是云端取证位置。仓库相对入口以上表为准；音频解码WAV未重复上传，原MP4已在仓库，复现数据与未上传项见 [发布范围](actual_audio/PUBLISHING.md)。

## S07新增静态素材

[正式原件](../../refs/anim_07_xiaoman_flop.png) · [独审](s07/independent/report.md) · [作者自检](s07/author/author_self_review.md) · [实际prompt](s07/author/prompt.txt) · [request](s07/author/request.json) · [来源manifest](s07/author/manifest.json)。

内置imagegen单次生成，原生1536×1024、1,684,116字节、SHA256 `35e9cdfdad8aa7aedb906d74a47c71d82dbf60c548938edc91a68012f309f77f`，底层模型未披露。独审与主审均实看，无必须阻止试接的具体解剖硬伤，可作仰躺终态。两手空是按剧本及当前要求，手机和插好的充电线应继续留在场景。抠除灰底时清浅接触影；按头身比例对齐后脑、肩背、髋和双手所在席面，不同姿态不能凭相同原生画幅直接等尺寸换图。翻身和扇风尚未验。
