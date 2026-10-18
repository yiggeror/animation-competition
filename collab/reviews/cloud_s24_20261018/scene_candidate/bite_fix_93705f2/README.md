# S24 · 修后静止咬合整镜与跨镜实证

沿 `155d25986b9d6bb38acc8f09043ca74922e4dd16` 的独立入口，只把 `sheet:(u,env)=>sheet23(3.4+0.1*u,env)` 一行改为 `sheet:(u,env)=>sheet23(5,env)`。运行依赖固定 **`93705f2f4d910a3b4805c602e8cc2c5bc2adda16`**，已读取并保留 [Opus原文](provenance/opus_93705f2_original_directive.md) 与修后共享源快照。实际用到的共享依赖相对155只有S23变化；没有在云分支修改共享S23、EDL、音轨或ready。入口旧SOURCE_SCENE_COMMIT/offset常量保留作原始记录，实际sheet调用已固定5；本次运行版本以 [运行清单](qa/runtime_source_manifest.json) 为准。整合时须与93705f2修后共享S23配对使用。

## 直接看实际片与切换

- [修后S24完整60帧MP4](actual_scene/S24_scene60_bite_fixed_1920x1080_24fps.mp4)：1920×1080、24fps、2.5秒、无音轨；一次全60帧实际Chromium渲染及编码。SHA256 `4c11a2c16fcf25e4b49fa69a5f078c2a75c22c65dff6b8a8767a4545c70ca55c`。
- [真实跨镜8帧小片](cut_evidence/S23_to_S24_actual8_1920x1080_24fps.mp4)：修后S23末118/119 → S24首000–005，严格原24fps，没有复制停顿或插帧。[切换片实际解码全帧](cut_evidence/00_actual_cut_fullframes.jpg)、[实际嘴喙近图](cut_evidence/01_actual_cut_contact_closeups.jpg)。S23仅另渲真实末两帧，[两帧源片](cut_evidence/S23_fixed_tail118_119_1920x1080_24fps.mp4)及原始Canvas/解码PNG一同保留，未渲整段120帧。
- [旧059脱口与新000/059对照](cut_evidence/02_old_gap_vs_fixed_first_last.jpg)、[新九曝光及末059的咬合实图](actual_scene/02_contact_across_all9_and_last.jpg)、[九态全景](actual_scene/00_all9_actual_scene_decodes.jpg)、[18个切换关键实帧](actual_scene/01_all_exposure_boundaries_actual_decodes.jpg)。相应完整解码PNG在 `actual_scene/decoded_keyframes/`；原始Canvas的000/024/040/059在 `actual_scene/canvas_keyframes/`。

作者已实看：S23末态与S24首态均咬住，换到床单背面后屏幕方向随机位反转，嘴喙接触继续；S24各曝光和末059不再脱口、幕上皮影保持静止。人物眼先动、整头连颈肩回看、微抬颏再落定仍沿锁图。此结论依据真实解码和局部，不用接点数值代替。见 [实看记录](qa/author_actual_review.json)。待Astra整镜原速终审与统一整合，未写共享ready。

## 锁图与核验

[九图SHA未变记录](qa/native9_baseline.json)逐张核对155原始Git字节，九张1024×1536人物PNG无更改；032=`cd01c1cc…e3e43`，040=`724d5c1c…16b8`。曝光、注册、相机、灯光、房间及幕布保持原入口，040右边缘两个原生黑描线切点仍保留，不冒称透明余量。原件/prompt沿既有人物锁包，生图调用0。

[完整核验](qa/actual_delivery_validation.json)包含新S24全部60帧原始Canvas SHA与对应解码MSE、S23末两帧及新MP4 SHA。S24最大RGB MSE为8.510557174682617。8帧切换片也独立解码逐帧核对来源，见 [映射](qa/cut8_source_mapping.json) 和各ffprobe JSON。

实际渲染资源审计中的九张PNG响应全部HTTP200并与锁图SHA一致，源PNG与浏览器实际帧SHA逐一对应。0 pageerror、0 requestfailed；S24有3条、S23有2条响应正文抓取缓存清除错误，NotoSansSC字体正文SHA未录入该轮审计，原始事件完整保留，未宣称零审计错误。另以独立浏览器做 **34项只读HTTP字节/SHA补核全部通过**，含两个字体，renderFrame调用0，见 [补核](qa/read_only_runtime_fetch.json)。控制台未标URL的404也保留，不推断来源。只读补核脚本首次相对导入路径误写，启动即失败，修正后成功；不影响两个实际渲染运行或输出。

复核工具和两条frames命令分别见 `tools/`、[S24日志](qa/s24_actual_frames_command.log)、[S23日志](qa/s23_actual_frames_command.log) 与 [命令参数](qa/render_commands.json)。完整原Canvas留在本工作区 `build/S24_bite_fix_93705f2_scene60/` 和 `build/S23_bite_fix_93705f2_tail2/`。未启动全片、Blender或新付费服务/API。
