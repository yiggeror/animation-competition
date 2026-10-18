# S08首38帧实际增量

[38帧MP4](S08_first38_1920x1080_24fps.mp4)：1920×1080、24fps、38/24秒、无音频，SHA `a33de1b70d8afb5f9db64bff4922858443c025198e6221b163cc5827ec499a2f`。

固定fa1c441e17d3848c4909d8a1c13fc9a5c1086427，入口`collab/reviews/20261018_2157_s08_first38_scene/s08_first38_scene.js`，SHA6a0d19cfaf66e849780b59aac766adcf33871b3ff0287ec0075542ac455220ca。仅1次成功实渲036–037两帧；前36张实际Canvas按2417653账本逐SHA复用，036严格持2帧，038以后未渲。组装编码1次，没有全38重渲。

已实看[035/036/037完整解码](00_actual_035_037.jpg)、[近手/侧管/低杆/灯芯2倍实际裁区](01_hand_pipe_wick_actual2x.jpg)，完整解码PNG在[decoded](decoded/)：近手与木柴在侧管前交越，红侧管被近手真实遮挡；火根(1335,785)在侧管画右接真柴头，不能称全程二维净空。远手仍扣低杆；桌上单盒薄影不增，灯芯受照但无火。指定局部作者门通过，Astra原速首38门待审，未报整镜ready。

[最短核验记录](verification.json)含38源SHA/逐帧编码MSE，最大9.45683；[复用36缓存账本](reused36_baseline.json)、[ffprobe](ffprobe.json)、[执行原文](increment_command.log)保留。39运行路径按固定Git/blob核SHA；盒层1665有效像素、alpha及可见RGBA与033全同，底970，body/arms无重复盒，低杆148像素盘与033逐RGBA一致。483像素归body为固定作者包来源说明，本轮未重新分层或改母图。[纯源合同检查](source_contract_check.json)核旧36的144子帧及038拒绝，和实际图像门分开。

本包只交影片、指定解码和短记录，不复制工程或旧证据。命令、Chromium进程配置见verification；真实PNG缓存保留在build/S08_first38_increment与build/S08_first38。生图0，S24人物、共享EDL、音轨、生产源及ready未改。

补交：[F036原始Canvas无损PNG](canvas_new/F036.png)、[F037原始Canvas无损PNG](canvas_new/F037.png)及[对应SHA](canvas_new/SHA256SUMS.txt)，从原build/S08_first38_increment逐字节复制，与首次verification.json逐帧账本SHA一致；补交生图0、重渲0，旧36帧未重复上传。
