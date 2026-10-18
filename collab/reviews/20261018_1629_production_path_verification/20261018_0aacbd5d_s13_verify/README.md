# S13生产迁移 · 十六起帧原字节实渲验证

**通过：新旧十六起帧实际PNG逐字节一致，解码RGBA最大差0；十六组资产及十项共享依赖也原字节一致。** 本次仅迁移检查，不生图、不改模块/音轨，不重复全镜表演审核；ready由协调登记。

生产固定`0aacbd5d4643c061ae56691f959ca5761f07a0b8`：新模块`js/anim/s13_drawn.js`。对照旧模块为已双审的`7b593c005451772d6e8192a8923fdfe18e64b781`中`collab/reviews/cloud_s13_20261018/full_scene/s13_drawn.js`。

**来源边界明确：生产提交没有旧评审目录。** 临时检出`/tmp/s13_render_assist_0aacbd5d`按原路径补入旧模块和十六张采用PNG，共17文件，均直接取7b593c00的git原字节；其余代码/资源一律生产0aacbd5d，生产已跟踪文件未改。[旧目录补档及资产/依赖映射](original_review_overlay_and_asset_map.json)保留17文件git blob、十六资产SHA和十共享依赖对照，未用重写旧模块来适配路径。

实际Canvas取帧`0/18/24/30/36/40/44/50/58/68/78/84/87/90/94/100`，两模块各16张，均1280×720。原PNG在`S13_new/`与`S13_old/`，已实看[实际十六起帧接触表](S13_actual_16_checkpoints.jpg)。[完整渲染/字节/资源记录](S13_render_and_resources.json)、[解码像素检查](S13_pixel_checks.json)、[模块仅SHEET路径差异检查](module_path_only_check.json)齐全。移除SHEET路径列表后两模块正文逐字节相同，曝光/人物注册/背景/鹤/光/颗粒均未改。

所有实际必需资源HTTP200，无pageerror或请求失败。另在浏览器原生fetch后核SHA，匹配各自明确来源commit的文件和git blob；十六新旧图像URL均实际解析，无占位或缺失跳过。唯一非必需favicon404单列。环境Playwright1.62.1 / Chromium154.0.8037.57，仓库dev/serve/renderPaint未改。

复查：`node collab/reviews/cloud_s13_20261018/render_assist/20261018_0aacbd5d_s13_verify/tools/render_s13_pair.cjs /tmp/s13_render_assist_0aacbd5d`。需先按映射将7b593c00旧17文件原字节放入临时生产检出；这是只读对照的来源准备，非生产改动。脚本记录实际模块、时间、输出SHA、资源URL/HTTP状态/响应体SHA和来源git blob。
