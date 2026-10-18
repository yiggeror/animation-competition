# S07 发尾修复固定2f6ae68e：仅18帧实际机位复验

固定源提交：`2f6ae68e1e2e959e25972d8785721435d51f87e9`。在独立detached工作树原样渲染模块，未改人物、手机、注册、机位或灯光，源工作树渲染前后干净。

- [实际18帧MP4](S07_tail18.mp4)：F039–056，1280×720、24fps、0.750秒无声。SHA256：`83b4b832a5ffa6db5bc4ac74e864b1c55235525cca9bcc94639144a64a30c3a9`，186273字节。
- 实际解码：[F039](decoded/F039.png)、[F043](decoded/F043.png)、[F046](decoded/F046.png)、[F049](decoded/F049.png)、[F053](decoded/F053.png)；对应视频本地索引0/4/7/10/14。
- [实际全帧接触表](actual_contact.jpg)、[手机/发梢3倍局部](phone_hair_contact_3x.jpg)；局部来自实际MP4解码，仅为观看放大，原尺寸裁切在 `phone_hair_crops/`。
- [原始渲染日志](render.log)、[ffprobe](ffprobe.json)、[视频清单](actual_video_manifest.json)、[固定源码及素材SHA](source_manifest.json)、[有效命令](render_command.txt)。

实看结论：五态中，手机在发梢下方露出的黑屏长边及边框可辨。F043真实前臂遮住手机右端，左侧/中部仍可见；不宣称整部手机无遮挡。五态红结与发根、发梢衔接连续，在实际720p与3倍裁切中未见明显灰孔或新断束。人物与手机位置保持原模块值，没有为露手机挪动物体。

本次只实际渲染F039–056共18帧，未重渲旧首25帧，未渲F025–038或F057–107。**此结果不代表整个S07完成或ready，交Astra判断本增量。** 没有图像生成调用或素材改绘。渲染日志含一条未标URL的404，实际请求的五态图及手机均正常出现，不记作零告警。

`--require`使用独立交付目录既有Chromium兼容垫片的绝对路径，仅为解析该文件；其余参数与指定命令一致。源码只读副本保存在 `source_module_readonly.txt`、`source_README_readonly.txt`。
