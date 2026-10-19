# S08 首49 · 仅新增046–048，撤柴后独立芯火实渲

固定源 `2360f4ec51535624342a066497ee1f9c6f0c666f`。入口 SHA256 `7440eae89753f3401f3217d39cb99bc5ce96b8ef77eee824fa422fe0e52ee489`；51个冻结输入核Git原字节及SHA，[清单](fixed_runtime_inputs.json)。采用此固定包唯一F046三层；未改任何源。

- [49帧静音MP4](S08_first49_1920x1080_24fps.mp4)，1920×1080、24fps、49/24秒。SHA256 `1c8a70dd8d086df70aa2f715b83bede2ff7bff393d562fb5ddacd9d0ad13a219`。
- 新增原始无损Canvas直接交：[F046](canvas_new/F046.png)、[F047](canvas_new/F047.png)、[F048](canvas_new/F048.png)，[完整校验和](canvas_new/SHA256SUMS.txt)，与实渲输出、合片前文件、浏览器PNG SHA全部相同。
- [045→048实际解码全帧](00_actual_045_048.jpg)、[两火6倍近图](01_separate_flames_actual6x.jpg)、[双手/侧管/低杆/单盒](02_hands_pipe_low_lever_single_box_actual.jpg)、[眉眼3倍](03_brows_and_eyes_actual3x.jpg)。四张完整解码PNG在 `decoded/`。

只1次实渲046–048、1次编码。000–045按 `07966095db7028677e884702cc784e69c172d0f2` 的已核原PNG SHA逐张复用，合片复制前后还核字节全等，[46帧清单](reused46_baseline.json)。旧043–045没有重渲，049不含。

## 实际画面门

已实看原始046与045/046/047/048实际MP4解码及局部：045柴火/芯火仍同根；046撤柴后，药头火在画左、固定灯芯小火在画右，两股火焰之间有清楚间隔。047/048芯火继续固定在芯顶，柴火跟药头；小芯焰可独立读出，不再只靠公式非零。两火都有各自根部，未见分裂成畸形双尖或黏连白团。

药头以实际冻结坐标(1350,782.572973)为根；近手柴仍在红侧管前，侧管在手后遮断关系清楚，远手单镯/低杆座、单盒与薄贴底影稳定。眉扬和眼神、指节轮廓保留，没有被白光吞掉。[作者实看记录](author_actual_review.json)。这是局部作者审，不代Astra导演签收或完整S08/声音终审。

全49帧源PNG逐一对照视频解码，最大RGB MSE=9.794037，[验证](verification.json)、[ffprobe](ffprobe.json)。辅助静态核184个旧子采样/46帧绘制、旧45层字节、灯/场景/火源码等；[结果](static_TEST_RESULT.json)，不冒充实渲。静态入口首次因稀疏检出缺旧包package.json而找错备用目录，原错误保全；补齐冻结基线后复核通过。只将该测试两份输出重定向到本包，源包文件逐一仍为固定Git字节，[核对](fixed_packet_after_static_check.json)。

## 实渲命令和网络

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first49/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0040_s08_first49_scene/s08_first49_scene.js build/S08_first49_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 1.9166666666666667 --to 2.0416666666666665
```

启动shim只指定系统Chromium和审计实际事件，没有修改渲染逻辑。[原日志](increment_command.log)、[实际网络](actual_network_events.jsonl)、[摘要](actual_network_summary.json)、[14个实际成功加载文件核Git字节](observed_runtime_fixed_bytes.json)。新046三层两页6响应均200；0pageerror/0requestfailed。实际console404位置为 `http://127.0.0.1:38739/favicon.ico`，response事件列表未捕获该响应，不称全请求200；历史first41未知404仍不倒推。

生图0，S12/S24新渲0；未改共享实现/留言/EDL/音轨/ready，不渲全片、不用Blender或付费API。
