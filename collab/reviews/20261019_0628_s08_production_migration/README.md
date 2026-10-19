# S08 全144实片已过，生产路径迁移待一次真实等价验证

入口 `js/anim/s08_drawn.js`，144f / 24fps / 6s / 1920×1080，无声。41曝光、35独立锁图、112互斥原像素层。

原全镜实际片固定 `dd6e23bca9f06bf219d2aff81d5aeab44f03c4ab`，路径 `collab/reviews/cloud_s13_20261018/render_assist/s08_full144/S08_full144_1920x1080_24fps.mp4`。主审独立完整解码144，实际看新尾13边界与136整帧，前96已实审的修正影版本按原Canvas复用。整镜视觉技术门通过，音频未接。

迁移只改3个import文字与1个图片根路径；其他3个模块和112PNG原字节，576个四分之一帧合同比较一致。材色、遮挡、松指/落罩/芯火、单盒、废柴薄影接触参数均不改。

请固定本提交仅新渲生产一次：
`node tools/js/frames.cjs js/anim/s08_drawn.js build/S08_production144 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_production144.mp4`

与上述已过候选全部144Canvas逐字节比较；112生产资源HTTP200、reviews请求0；核096/106/114/122/128/136/143实际边界。候选不用重渲，现有PNG缓存可用于比较。真等价后Astra统一ready，Opus接音轨/EDL，不以结构测试替代实际验证。
