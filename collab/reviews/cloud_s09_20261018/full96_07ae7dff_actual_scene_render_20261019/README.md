# S09完整96帧实际实景渲染

固定生产源 `07ae7dff749abd53394e05b1c37f232afee67791`，独立交付分支 `cloud/s09-full96-render-20261019-07ae7df`。仅执行一次完整S09镜头渲染；未启动全片、未重画或修改生产实现/EDL/音频/ready。

实际完整片：[S09_full96_07ae7dff_1920x1080_24fps_ACTUAL.mp4](S09_full96_07ae7dff_1920x1080_24fps_ACTUAL.mp4)，1920×1080／24fps／96帧／4秒／无声。SHA256 `6d3d244ae703c024f4af5e79e71da2e41fac8f70761902e00196badaf3ae1b15`，与build/S09_full96.mp4逐字节相同。

README指定39张换态帧均从这个实际MP4全分辨率解码保存于decoded_actual_mp4/，四张ACTUAL_required39_full_scene表按序覆盖全部39张，作者已全部实看。另有第一次推键失败/退档、两次触掌与回弹、058→060→062→063整桥、双手整筒、072→073首次亮、077/085完整头颈专项实图。6.1sol独立实看专项表和原尺寸解码帧。

有限实看结论：两次尾盖接触掌垫后均重新离掌；062真实红筒/键面完整，没有旧孔和双键；完整可见双肘在画内，头颈未见新重影/透明缝。072仍暗、073首次灯面及向画右单光束出现，尾组持续亮；077确认及085向右头态区分明确。未见新的实景阻断。逐张换姿仍可读，不能用静态接触表代替整段节奏/时间流畅终审；交Astra，不自行宣称整镜最终通过。

20曝光态连续覆盖000–095，原23张生产人物/发光PNG在渲前后SHA全同。96张原渲染无损PNG仍保留build/S09_full96/，逐帧SHA与曝光源绑定在actual96_render_decode_and_resource_checks.json；另将实际编码片全部96帧降采样解码并与对应渲染PNG逐帧核对，最大RGB平均误差2.028LSB（包括视频压缩和缩小差异）。这项编码顺序核验与39张原尺寸实看分开记录，不冒称自动语义通过。

资源日志：62项request/response均200，23个生产人物/发光路径全部实际加载，reviews路径请求0；无requestfailed/pageerror。唯一console404为favicon.ico，与镜头素材无关。详见resource_checks.json、browser_resource_summary.json、browser_resources.jsonl和render96.log。

实际渲染命令原样：`node tools/js/frames.cjs js/anim/s09_drawn.js build/S09_full96 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S09_full96.mp4`。环境仅用本目录capture_browser_resources.cjs预加载系统Chromium：NODE_PATH=/opt/codex/cua_node/lib/node_modules，NODE_OPTIONS=--require=<本目录绝对路径>/capture_browser_resources.cjs。原Playwright缓存浏览器缺失，生产文件未改。decode_and_check.py只核既有片/解码和制证据图，不再渲染。

固定协调README/源索引/结构与灯层检查快照以FIXED_COORDINATOR_前缀保留；本次素材来源、完整SHA和全部96帧绑定在source_before_render.json。新生图调用0、原始图输出0、重试0；现有绘图提示词及原始输出按各锁态来源继续保留，不重复打包。
