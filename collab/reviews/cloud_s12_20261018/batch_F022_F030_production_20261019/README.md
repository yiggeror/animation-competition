# S12 022→026→030 执行 · 停在022首触缺失

按1651ff2批次独审的执行补充修订请求后，仅调用**F022一次**，原件返回后自审发现重大接触错误，按停止规则停段。026/030未绑定、未调用；无重试、无像素修补、无新场景渲染。

[022原件](originals/F022_raw_call01.png) SHA256 `938682ddf40b13e6b72dbacbabedf9502ae73bba79944b330aae6a3bedb26234`。工具原文件`/workspace/generated_images/exec-3ff078f9-8184-4974-90fc-fd68f096471e.png`仍保留，交付副本字节一致。已实看原件、[018→022同尺度](qa/018_to022_actual_same_scale.jpg)及[完整臂/双手/固定7px杆诊断3倍](qa/F022_complete_arm_fixed_rods_DIAGNOSTIC3x.jpg)。

**拇指没有首触：**整只远手的可见实际墨线/AA（alpha≥8）距冻结上签外轮廓仍约**30.062场景px**；最近原生像素(974,908)，实际可见手部最下缘y910；目标T_SURFACE在(975.093564,952.418887)，其邻域无alpha≥8人物像素。[短自审记录与实际mask](qa/F022_self_review.json)。这是未到杆面的悬空手，不是合格022；不能作为026母态。未签未来分层或接触段场景通过。

调用前已冻结[完整真实请求](requests/F022_call01.json)和[完整prompt](prompts/F022_EXACT.txt)：prompt SHA `4a52fe928eb32725d3ee394a346aa70a5a7d50934f1f172b86f753612b46f79f`；request SHA `712de4c70f81349e6831f5842f4e12f7c976d7ee75f771a832b5ba72df440240`。首句母态正确为锁018/c63f57f5…ff40be；已按补充加入P/G_AXIS/T_SURFACE区别、仅拇指首触边界、忽略材色板旧012 footer、禁止未获批的后续抬偶。实际三输入及SHA在同请求内，未新增竞争旧全身图。

[026模板](requests/F026_TEMPLATE_NOT_BOUND.json)只等待真实合格022，首句身份为F022；[030模板](requests/F030_TEMPLATE_NOT_BOUND.json)只等待真实合格026，首句身份为F026。两者`tool_arguments:null`、执行关闭，绝未以旧018冒充它们的实际母图。绑定脚本必须校验前态`ACCEPTED_FOR_NEXT_CONTINUITY`与实际PNG SHA，当前失败记录不满足继续条件。

[调用账本](provenance/call_ledger.json)：022=1、026=0、030=0；原件1、在飞0、已接受态0；S12累计调用6。原件、请求、冻结SHA和工具返回原文均保全。只新增此独占目录至`cloud/s12-reference-20261018`，未改旧包、共享实现/留言/ready/EDL/音轨；S08仍待整段。
