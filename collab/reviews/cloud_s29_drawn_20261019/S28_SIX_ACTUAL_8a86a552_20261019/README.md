# S28 固定8a86a552：六张实际浏览器关键帧

原作者可直接取 `stage/F000_png.png`、`F012_png.png`、`F042_png.png`；手机为 `phone/F132_phone.png`、`F162_phone.png`、`F191_phone.png`。六图1920×1080已实际打开；原偶条带已消失，042回落臂入层，132首张已有充电图标，162/191继续推近。只交六关键帧，不代替完整192门。

固定源码 `8a86a552fba1a822aae0f27ca53e2b0defb4e392`，独立只读工作树干净。依两份README，在8196跑新版float `render_three.cjs`，结束后才在8195跑原末插 `render_phone_three.cjs`；无并发共享S/GL。新版完整入口 `float_depth/entry_full192.mjs` 已记录SHA，未用旧8bit舞台跑三图。手机按用户指定原末插命令，其phone_insert与新完整入口委托相同。

舞台三帧均报告 `RGBA32F/NEAREST`、`floatMatUploads=1`、原program槽未改、GL/DEBUG/场景proxy恢复；042 `depthWeight=1/localArmMask=42`。原样 `RENDER_SELF_CHECK.json` 与 `PHONE_THREE_CHECK.json`、标准输出日志随包。舞台日志有单个404控制台消息，原脚本无URL日志，未冒称具体资源。

各帧foreground/shadow随包，共12张原样输出PNG，完整SHA见 `SHA256_ACTUAL_12_PNG.json`；源脚本／适配器／新入口SHA见 `SOURCE_FIXED_SHA.json`。没有复制25图、追加生图、渲整段或修改共享实现。根审查记录保留有限脚影及连续帧未验局限。
