# 奶奶短签 v2 局部修订交接

执行方式：内置 image_gen.imagegen，一张图恰好一次调用。输入仅为本目录原始 anim_20_grandma_puppeteer.png；没有输入小满、裁图或其他角色图。

编辑范围：按既有独立审查，仅去掉较低裸腕手掌后朝左下露出的错轴金黄短尾；请求保持掌前短签、握指和拇指、手臂、上手和签、身份服装脚位及 1024×1536 画布。没有生成掌内整根杆，没有代码改图。

输出：anim_20_grandma_puppeteer_v2.png。实际完整提示在 v2_prompt.txt，实际工具参数在 v2_request.json，原始完整工具返回（包含 image_url）在 v2_tool_response_complete.json，工具来源在 v2_tool_metadata.json，尺寸、字节、SHA-256 及来源一致性在 v2_file_verification.json。

已实际查看输入与输出全图。两张 PNG 的保存文件均与工具源及返回 image_url 解码后逐字节一致，格式 RGB PNG，1024×1536。v1 哈希保持原审查记录不变；未改仓库。

原 v1 已按带风险的接入试验素材使用。本 v2 是供独立验收后明确替代 v1 的候选，不回写或改判原 independent_review.md。是否替换仓库及实际卡片，由协调方与 Opus 在独立验收后处理。

独立验收待办：实际查看 v2 近侧下手，确认尾段已去除、掌缘自然、握指/拇指/掌前竹签完整；对照全图确认无非目标明显漂移。作者不作通过判定，不新增生成调用。

