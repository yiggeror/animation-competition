# S14 挂灯最小接入候选

仅独立候选，不修改共享仓库/index，未发布，未实际CAM渲染；不能替代生产门审。

## 已实现
- `lamp_close.mjs` 导出 `makeLampClose` 和 `exposureAt`。使用已采用的1200×1140整组件PNG，不重注册、不分肢。
- S14绝对时间4.0秒至5.5秒之前：096/102/108/114/120/126各6帧；095和132及其他帧返回false，不触碰ctx。
- 同一source [190,100,1600,900]等比映射16:9。禁止非16:9拉伸。
- 原S08灯几何/火苗函数，原点本地化；仅离箱后关闭接触阴影。120/126保持(860,737)，前钩弧遮挡承重柄线。
- 缺真实后台/灯光回调即报错，绝不静默使用占位背景或技术平底。
- `node test_adapter.mjs`：240帧范围选择、36帧曝光、矩阵、回调次序、外部帧不触碰及缺依赖拒绝通过。Canvas/Path2D为mock，明确不是实渲证据。

## 原接口已核实与缺口
已保存S14 `renderFrame(ctx,t,W,H)` 内调用私有shot/sheet，无法单独导入后台层，且旧版T_LAMP=5.0不得作为新方案时序。paintshot导出loadImg/placeholderBg/renderPaint，其中placeholderBg不是实际背景。S15 makeShot包装整镜和光学链，不提供可复用后台近景函数。本候选不导入、不修改S15。

必须由现有生产工程绑定两点：
1. `drawExistingBackstage(ctx,{t,exposure,viewport,curtainLit:false})` 在已设置的局部源坐标中绘制原后台、原箱体（箱顶y980）并覆盖[190,100,1600,900]。原图右界1200以外590源像素，即输出708像素，须从既有后台取景或延展，不画新房间/新道具。不能在回调里再画第二只灯/第二只手。
2. `applyExistingLight(ctx,{t,exposure,viewport,lamp,curtainLit:false})` 复用既有灯光与材质通道。调用时仍为源坐标矩阵，不能套用整镜未变换的光源坐标。此回调负责原火光与背景/原画一致，不允许把本包平光诊断当最终光照。
`loadAdopted(id)`只加载publication_lamp_close/adopted/{id}.png，不加载含底图static文件。

## 精确调用点示意（非可盲贴旧S14的完整补丁）
初始化一次：
    const renderLampClose = makeLampClose({loadAdopted,drawExistingBackstage,applyExistingLight});
在已批准S14 renderFrame最前面：
    if (await renderLampClose(ctx,t,W,H)) return;
    return existingApprovedS14RenderFrame(ctx,t,W,H);
其中existingApprovedS14RenderFrame必须保持已批准整镜，幕亮门从132/5.5s开始，不能回退到所存旧模块的5.0s。S15模块/原灯外形/原光学世界坐标完全不改。

## 必须实际核验的四组
095/096（入近景）、119/120（挂钩承重）、125/126（松手灯固定）、131/132（5.5s幕亮切出）。原技术36帧片仅局部动作诊断，不构成上述切镜通过。

03:05 静态独审硬化：真实后台回调单独save/finally restore隔离CTM/alpha；灯块也用finally恢复。`node test_state_isolation.mjs` 验证后台修改CTM/alpha不污染后续，后台/灯块入口/灯光回调抛错后适配器栈恢复。该测试不是原灯内部每个Canvas调用的故障注入，真实浏览器实渲仍待工程绑定。
