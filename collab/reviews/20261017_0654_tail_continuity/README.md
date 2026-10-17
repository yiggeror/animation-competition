# S29/S30带声新尾、S14夹布图与停电连续性增量

本批实际影片均960×540/24fps。沿用原JS项目，未重启旧Blender，也未替换为12fps旧片。仍属可审整合版，完整动作与全片输出尚在推进，不是正式成片。

## 先看这些文件

- [S29→S30同版带声24秒](clips/S29-S30_continuity_24fps_audio.mp4)：奶奶包布收口、小满看手机/抬头，奶奶靠近灯准备吹；电视先关，拉绳关日光灯，切大头影憋住。也可单看[S29](clips/S29_24fps_audio.mp4)、[S30](clips/S30_24fps_audio.mp4)。
- [S04→S05同版带声12秒](clips/S04-S05_continuity_24fps_audio.mp4)：停电之后切手机，开镜即1%无充电闪电。[新版S05](clips/S05_24fps_audio.mp4)只改变前12帧状态栏；手和14次连按保持。
- [S14奶奶夹布原件](../../refs/anim_14_grandma_hang_sheet.png)：原生1024×1536，内置imagegen首稿加一次限定迁镯编辑；底层模型未披露。新唯一绿镯在实际左腕，右腕裸。实际prompt/request/hash及两级审查见本批s14_grandma目录。

## 本轮实审结论

[S29/S30作者](blow/author/author_report.md)与[独审](blow/independent/report.md)绑定两支新完整静音MP4。S29前240帧、S30前190帧原字节复用，新尾分别实际重渲48/98帧；独审复核576帧hash、430张复用帧和34个依赖，并逐帧实看新增区间及切点。近景灯框不再挡嘴，鼓腮和小火苗可读；灯与头的世界位置相同，前后台左右反转符合两侧机位。大头影由真实alpha投影，未贴屏幕假影。

本候选仍省略奶奶起身转身、逐件收偶/折鹤颈，小满步行到门边/落跟。S30尾头影约4.08秒保持已可读；与S31连看后发现原S31背景提前出现鹤、奶奶未回应的问题，正在补泄气笑与退出，并提前小满晃龟邀请。**本批S29→S30联片不将尚未完成的S31反应一并报通过。**

[S04→S05小项独审](phone_continuity/independent/report.md)关闭了真实因果错误：S04+0.6秒停电，S05切入已过7.4秒，旧片仍显示6帧充电/12帧2%。现前12帧全部1%无闪电，像素变化仅状态栏，手/机身/游戏框外逐像素相同；后84帧原PNG逐字节复用。96帧非status状态和F12起完整状态也独立复算相同。本条不重启已通过的手机手部修订。

[S14 v1独审](s14_grandma/v1_independent/report.md)记录错腕；[v2独审](s14_grandma/v2_independent/report.md)确认关闭。v2有少量非目标描线/纹理重绘，不称像素锁定。人物全身、夹布接触可用，单侧踮起伸手瞬间；接景后仍需看前掌落地、衣夹与现铁丝锚点，不能称完整搭布/挂灯动作。奶奶接入与小满站立拖凳新图正在推进，后者PNG已生成、尚待独审，不计作通过。

## 当前母带：去掉S31多余开手电声

剧本明确手电一直亮着。bce6789已使S31开镜照脸即亮并清灰筒残片，同时删掉audio中S31+0.6的多余click。新[WAV](audio_no_extra_click/film_mix_norm.wav) SHA256 `6980ce06f50f6348b8f832d23cfb4a5d72edddda61ab47ade274727ecaaf18c4`，实际-16.04LUFS/-4.40dBTP；[全片AAC](audio_no_extra_click/FULL.m4a) SHA256 `4bf872384ba2bec30dbd81b75fc9668da7571052bf81486c276573048f5b9f2d`，实际-16.08/-4.20。

[实际33项测量](audio_no_extra_click/measurements.json)包含WAV、全片AAC及31镜独立AAC；最高真峰为S08的-2.46dBTP，均满足≤-1.5。源快照与构建日志齐，删除合成调用后未假称其余PCM逐样本不变，而是重新编码/测量全部。245.5秒含当前244.5秒EDL及1秒尾缓冲，尾缓冲非静音。

[前一TV/fan母带独审](audio_previous_independent/report.md)仅绑定旧101d818f/201820c3版本，其中仍有S31 click；新去click版正在独立差异复核。两版都没有主观听审，数值不等于听感合格。新联片音轨均使用本批6980ce06母带，命令/切段点/hash见[clips manifest](clips/manifest.json)。

## 保存与交接

独立实现分支 `codex/astra-integration-20261017` 已保存：19b9905为S29/S30和EDL绑定，bce6789为S05状态连续、S31手电与多余click修正。已读回[19b的15个代码/素材/EDL/登记文件](remote_readback/19b9905.json)及[bce三项源码](remote_readback/bce6789.json)，全部字节一致；[上一collab批次a6bb100读回](remote_readback/a6bb100.json)也附。原协作分支只追加collab，没有改Opus留言或覆盖实现。

全部31项现在有模块绑定，但S14等仍有未完人物动作，模块数不是完成量。现正从固定源快照渲染其余同版24fps镜头，既有实际24fps文件经源核对复用，最终再核连续剪辑。旧249秒12fps粗剪仍没有冒充新成片；新全片文件尚未完成。

本包保留实际视频、来源hash、完整审查和必要原像素证据；不重复上传可由MP4恢复的全部PNG帧。报告中的工作环境路径保留为审查现场记录，可下载对象尽量改为仓库相对链接。
