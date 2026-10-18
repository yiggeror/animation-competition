# S01 生产路径迁移：指定17帧零差验证

新固定`38a5302d58a9c845600a496b478cefb3e657e74a`，对照旧固定`ab3644e096c0f9d94b5053f7c136ef515107e4b8`。只新渲1280×720的0/10/12/20/28–35/43/50/62/70/83，共17帧；旧参照为上次完整84帧渲染保留的原始Canvas PNG，未重新全镜渲染或重审观感。

- **17/17 PNG逐字节相同，RGBA解码相同，变化像素0，通道最大差0。** [逐帧原/新SHA及像素结果](pixel_comparison.json)、[共同像素值的实际PNG](frames/)。
- **18张角色PNG、时间线逐字节相同。** [静态检查](static_migration_checks.json)。新模块仅两处相对路径替换，正规化后与旧模块整文件相同：[diff](module_path_diff.txt)。
- **实际模块/背景/PNG资源HTTP错误0、请求失败0、页面错误0、控制台错误0。** [资源状态](browser_resources.json)、[渲染日志](render_selected.log)。探针只为浏览器favicon.ico预设本地204响应，未替换任何场景模块或图片响应。

迁移源工作树前后干净。没有改模块/音频、没有生图、没有写ready；此包仅是路径迁移等价性验证。

复现：在固定38a5302d工作树作为cwd运行 `node <本目录绝对路径>/render_selected.cjs <固定工作树绝对路径>`；然后在保留旧84帧原始PNG的同环境运行 `python compare_selected.py`。脚本与结果均随包。
