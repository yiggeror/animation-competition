# S29 后段动作增量（11 张采用画）

本包 11 张 PNG 已逐一核对原独审 SHA-256，均相符。仅为后段集成候选，不能替代整镜原速连续性验收。原始生成材料已保存在 Library：libfile_bd643b9a92788191ae69d76acc98b87b，本包不重复原件或视频。

## 应用前提
必须使用原完整 S29 接景并已完成花衫色修的工作副本（来源读取 f8ada6aa3a11bc251c265885bb2bedd618d45077，原完整基线 d7f6a646991506712f9d4bf13a1d4dc3fa132df0）。本包不是可独立运行场景；补丁仅包含 js/anim/s29/wrap_tail.js 的曝光差异，不包含完整 body、loader、正式入口或旧采用图。接收端必须已有正式 js/paint/shots/s29.js 入口、wrap_tail.js 加载逻辑、前段人物和原尾段 lift/lowering/contact/settled 图及其色修。不要在裸分支上直接应用并声称可运行。

将 assets/chars/s29_tail/tailfix_*.png 按相同相对路径置入工程；在完整副本根先执行 git apply --check，再应用 S29_TAIL_MOTION_ENTRY.patch。若同模块已被前段作者修改，只按差异合并后段曝光，不覆盖完整文件或回滚前段。PNG 为原 1024×1536 坐标内采用件，不附加新整人变换，沿现 loader/scene 注册消费。

## 边界
实际动作变化限 F132–187；F188–239 回到原 settled 终态，不改其图像。EXPOSURE.json 的 scope 132–239 是尾段表范围，changed_frames 132–187 才是本次变化范围。F000–131、F240 起近景、原手机时点、小满转头、相机、音轨、12 秒/24 fps/288 帧 EDL 均不在此包修改范围。F149–153 lowering、F172–178 contact 仍依赖旧色修源；不是 11 图独立全覆盖。

按此增量接入后仍须真实场景原速核前后衔接与时长。本次交付准备未重新渲染，也未增加动作画或重新计数。
