# S08 首53 · 新增049–052四帧实际渲染

固定 `e94e1f19894dba379f79533dd6b263e7509cff2f`；入口 `collab/reviews/20261019_0123_s08_first51_scene/s08_first53_scene.js`，SHA256 **`976324d973c85ece7eb51e17b17c2d7adcfd630e5da8b1d0cb0f75281076dbbc`**。固定提交已从origin取回，源包 **76/76文件** 在渲染前及审计后逐字节核Git一致，[读回](fixed_packet_readback.json)。使用 `RUNTIME_ROWS_FIRST53` 的54项，[运行输入](fixed_runtime_inputs.json)。没有改源。

- [53帧静音实际片](S08_first53_1920x1080_24fps.mp4)，1920×1080、24fps、53/24秒（2.208333秒）、单视频流。SHA256 **`311800f58d82624235d6549d113569ee48b47ace8ce7496f4b201ff0453fc142`**。
- 新增四张原始无损Canvas直接交：[F049](canvas_new/F049.png)、[F050](canvas_new/F050.png)、[F051](canvas_new/F051.png)、[F052](canvas_new/F052.png)，与实际输出、合片前PNG和浏览器PNG SHA相同，[四张完整SHA](canvas_new/SHA256SUMS.txt)。
- [048→049→050→051→052实际解码全帧](00_actual_048_052.jpg)、[真柴根/固定芯火4倍](01_match_and_fixed_wick_actual4x.jpg)、[双手/前后侧管/低杆/单盒2倍](02_hands_pipe_low_lever_single_box_actual2x.jpg)、[眉眼3倍](03_brows_and_eyes_actual3x.jpg)。对应五张完整MP4解码PNG在 `decoded/`。

**只1次增量实渲049–052，1次编码。** 旧000–048按 `707764d22518caee7712eb006361bc1d2ebfc79e` 的真实无损PNG清单逐张核SHA，复制后再核字节全同，[旧49来源](reused49_baseline.json)。没有重渲旧49，**F053不含**，也没有提前灭柴。

## 实际观察与复用边界

实际打开原始049/051与五帧真实视频解码/近图：048→049下甩读得清，050→051反摇回上位；近手与手中真柴一起移动。049/050药头位于(1352.193621,825.739360)，051/052返回(1350,782.572973)，火焰根跟药头，旧位置没有留下悬空火。芯焰固定在(1415,794.572973)独立续燃，两火全程有各自根部与分离间隔。

近手柴仍在侧管前，远单镯手/低杆座、箱盒单份和薄贴底影稳定；眉眼、手指与指节轮廓保留，未见合成白团吞掉结构。[作者实际看图](author_actual_review.json)。这是本段作者复验，完整S08及声音终审仍由Astra整合。

F051×2 **精确复用的是F046整组三个原生图层**：EXPOSE直接引用asset046，不是新PNG，不是孤手层变形；当前固定源已核无051新图文件。051/052按各自绝对时间继续原火/光曲线，因此不把整幅Canvas等同046历史Canvas。[固定源逐帧参数](source_048_052_samples.json)只是辅助；可辨火焰依据实际片。

[原像素回归](source_original_pixel_checks.json)：桌盒1665可见像素、alpha与可见RGBA同046、底970；低杆盘按像素中心取148px，049/046RGBA全同；arms在y≥981无alpha。原首51静态核旧49的196子采样/48旧图；首53静态核旧51的204子采样和051/052整组046复用，[首51](static_TEST_RESULT.json)、[首53](static_TEST_FIRST53_RESULT.json)。这些不是Canvas证据。静态测试报告写入重定向到本独占包，源76文件复核不变。

53帧源PNG与视频解码逐帧比对，最大RGB MSE=10.012828，[验证](verification.json) / [ffprobe](ffprobe.json)，未把有损解码称无损原图。

## 命令与实际加载

```sh
NODE_OPTIONS='--require ./collab/reviews/cloud_s13_20261018/render_assist/s08_first53/tools/network_audit_chromium.cjs' node tools/js/frames.cjs collab/reviews/20261019_0123_s08_first51_scene/s08_first53_scene.js build/S08_first53_increment --fps 24 --w 1920 --h 1080 --workers 2 --from 2.0416666666666665 --to 2.2083333333333335
```

[原始命令日志](increment_command.log)、[实际网络URL/状态/console位置](actual_network_events.jsonl)、[摘要](actual_network_summary.json)、[实际成功加载文件逐字节核固定Git](observed_runtime_fixed_bytes.json)。049三层与051回用046三层各两页6次响应均200；0pageerror/0requestfailed。实际favicon404的console URL保留在摘要，response事件未捕获该响应，不宣称全部请求200，也不倒推历史未知404。

生图0，未动S12待审包、共享实现/留言、ready、EDL或声音，未渲全片/053+、未用Blender/付费API。交付仅此独立目录，推送前同步私分支并记录；不推生产分支。
