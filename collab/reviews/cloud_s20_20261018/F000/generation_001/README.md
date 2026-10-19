# S20 F000：唯一一次首母原件回审

基于 Astra 对 `d783004174847be5685124a0920b75cbadf8cc83` 的双审放行，仅执行 F000 一次。提交前核得本线程/本镜记录 **0 在途、0 历史调用**；本次 **1 工具调用、1 原件、0 重试、当前0在途、后态0调用**。未启动场景或全片渲染，不改原216帧、切点、EDL、声音或生产代码。

## 单张交付

[原始PNG：S20_F000_call001_raw.png](S20_F000_call001_raw.png)，1672×941 RGBA，无改像素。SHA256：`de1aec591119393f7f99a61a166f62e9af456ce24ffd718fec0429b20fe2e330`。

[灰底全身实看](qa/gray_matte_preview_QA_NOT_OUTPUT.png)仅供检查透明边缘，不是人物层替代品。原工具路径 `/workspace/generated_images/exec-e7aa8f1c-8b83-4d91-9957-f6db7978b813.png` 保留，交付PNG与该文件及完整工具返回中的图像载荷逐字节相同。

| 对象 | 本张实际持有/接触 | 放大检查 |
|---|---|---|
| 奶奶解剖L，单玉镯、高位手 | C_N+C_B两鹤签；拇指/屈指握住两根直杆 | [L手与杆尾](qa/grandma_L_crane_grip_gray_QA.png) |
| 奶奶解剖R，无镯、低位手 | T_H+T_S两龟签；袖—肘—腕—掌连续 | [R手与杆尾](qa/grandma_R_turtle_grip_gray_QA.png) |
| 小满R、L | 两只开放掌，持杆0、接触0；与杆可见空隙 | [双掌](qa/xiaoman_both_open_hands_gray_QA.png) |

作者实看：两人身份与成人/孩子比例可读、完整全身；四根竹色杆可数，握持及露出短尾未见明显折轴/分叉；施工记号已去除，使用中性固有色与自然体积阴影，无场景光斑。此为画面内目测，不称已通过 CAM20 实景透视或真实骨长测量。详见[逐项实看记录](author_visual_review.json)。

透明通道经灰底实际合成检查正常。原件在主体外检查域有346个alpha=1的极低透明度游离像素，本轮未清理、裁切或改色；[PNG实测](qa/png_inspection.json)保留该限制。

## 原请求与来源

- [Astra授权原文](authorization.json)、[提交前0在途证据及其范围](preflight.json)、[当前单次状态](status.json)。没有服务端全局队列查询能力；0在途依据本线程和本镜本地记录。
- [实际提交的完整参数](request_submitted.json)、[完整提示词](prompt_zh.txt)、[完整原始工具返回](tool_return_original.json)。仅使用 `image_gen.imagegen`，底层模型版本未由工具披露，不作推测。
- [实际5输入的冻结快照与来源/SHA](submitted_input_snapshots.json)，快照均在 `frozen_inputs/`，与提交时的真实路径字节相同。原[准备清单快照](frozen_input_manifest.json)中的0调用是提交前历史状态，当前计数以本目录 `status.json` 为准。
- 唯一姿态输入SHA为 `7bb8cc5b12cd86ca6b621425dca90e9cb878f3ba04c9160b4948098d5c777aee`；其余四图只提供两人身份。未输入F020，不用交接中态代首母。
- [交付验证](verification.json)、[全文件SHA](SHA256SUMS.txt)。QA图只作诊断，原PNG未改；没有新增修图或第二次模型调用。

当前为 **作者实看通过，待Astra单张审查**。仅冻结方向、相对站位及首握状态；实际CAM20、偶端世界投影、接景前后遮挡仍待核。未制作任何后态，不登记ready。
