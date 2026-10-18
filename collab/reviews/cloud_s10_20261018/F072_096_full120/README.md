# S10 八态齐全：072/096尾两态与实际120帧，交Astra复审

已按00711c72后的锁定指令，沿045绘制072，再由072绘制096。两态均采用真实图像工具返回的完整头颈，保持画左视线，随回转恢复远耳和镜架透视；未用代码挪动五官。20°/14°是构造目标，不冒充二维图像精确角度测量。

## 交付入口

- [完整模块候选](S10_drawn_full_candidate.js)：5秒，24fps，八态曝光24/3/3/3/12/27/24/24；基础画1920×1080，使用`closeShot`及`sc:1`，没有额外人物缩放。
- [八张采用图](adopted/)：[000](adopted/F000.png)、[024](adopted/F024.png)、[027修版](adopted/F027.png)、[030](adopted/F030.png)、[033](adopted/F033.png)、[045](adopted/F045.png)、[072](adopted/F072.png)、[096](adopted/F096.png)。全部与模块所引用原路径逐字节一致，映射见 [曝光及SHA表](S10_adopted_exposure.csv)。
- [完整实际实景MP4](exposure/S10_full120_scene.mp4)：1280×720，24fps，120帧，5秒，无音轨。SHA256：`8ed53dc47f7bcd4912b2d3ac85e23cc261c4db3c6804ebdc1d3d3107ea5ae223`。
- [实际MP4解码接触表](exposure/actual_full_scene_contact.jpg)、[20张原尺寸解码帧](exposure/decoded/)、[尾三态头颈对照](qa/tail_head_sequence_contact.jpg)。
- 新原件在 `originals/`；完整提示词、实际请求、输入SHA及工具返回来源见 [调用清单](provenance/call_manifest.json) 和 `provenance/`，前六态旧原件及提示词保留在同一独占根目录的原批次中。

## 短检查

1. 真实图像已实看：045→072→096整头、耳、镜架、下颌及颈部连续回转；两眼始终向画左，尾态较峰态缓和。双手/肘/腕均在画外，冠顶及盘发完整。
2. 八张采用PNG均为1920×1080 RGBA，y948–1079底部衣带逐像素零变化；采用副本与原渲染路径SHA一致。新输出原件未改，源RGB及alpha>24未被清理。
3. ffprobe实际计帧120，时长5.000秒，无音轨；MP4独立解码实看000/021/022/023/024/026/027/029/030/032/033/044/045/071/072/083/095/096/108/119。
4. 实际浏览器渲染的000–071与已通过72帧版逐帧PNG字节完全一致（[核对记录](qa/approved_prefix_comparison.json)）；072后在场景灯光层继续退光，108起手电光为零，人物纹理没有画死的光斑。
5. 后领原有几像素毛边按Astra实审结论保留，未重画已锁头态。渲染日志保留单条未标URL的404，无模块/图像加载失败；未将其写成零告警。

新两态和全5秒灯光节奏仍交Astra复审，不自行签全镜或音轨。本批图像调用2次，实际返回2张，工具失败0次；S10累计11次。未改共享实现、ready、留言或音频，未处理S07。

复现（仓库根目录）：

```sh
node --require ./collab/reviews/cloud_s10_20261018/render_assist/use_system_chromium.cjs tools/js/frames.cjs collab/reviews/cloud_s10_20261018/F072_096_full120/S10_drawn_full_candidate.js build/cloud_s10_full120 --fps 24 --w 1280 --h 720 --workers 4 --mp4 collab/reviews/cloud_s10_20261018/F072_096_full120/exposure/S10_full120_scene.mp4
python collab/reviews/cloud_s10_20261018/F072_096_full120/exposure/decode_actual.py
```
