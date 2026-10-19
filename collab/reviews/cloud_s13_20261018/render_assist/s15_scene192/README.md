# S15 实际三帧机位门｜人物过低，暂停192帧

固定源 `5271da8b1870bf4523cd7bb4eaf101f77147d6d8`，24路径逐字节与Git核对。实际一次浏览器会话只渲 F000/F132/F144；[三帧实景](preflight/three_actual_framing.jpg)，完整无损原Canvas为 [F000](preflight/F000.png)、[F132](preflight/F132.png)、[F144](preflight/F144.png)。

三帧均实看：候选16.5px/cm注册使小满处在左下方，胫下段、鞋及凳腿明显被底边裁掉。按Astra指定门暂停整192f；未自行改整人物、头或相机，也未改变原鹤幕。等待Astra裁定整人物注册后才能继续。

[实际核验与资源摘要](preflight/FRAMING_REVIEW.json)、[原资源日志](preflight/network_events.jsonl)、[固定24路径](fixed24_readback.json) 及单会话脚本齐全。三个Canvas SHA与浏览器返回一致；成功加载文件均与固定Git原字节一致，0pageerror/0requestfailed。未生成新图，未渲全192f，无重复工程上传；仅本独占交付目录，私分支 `cloud/s15-actual-render-20261019`。
