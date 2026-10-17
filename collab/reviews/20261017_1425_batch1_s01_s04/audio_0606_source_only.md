# 0606d3a S03音源改动补核（源码层关闭）

root提供0606d3a；未运行Git。当前audio/build.py SHA256 `6d6b93929cf0f77f125c324eeee700d1f6356c6063ec6cf494d46d1cf41de0fb`。与68071b1冻结源作文本diff，唯一改动是216行将S03 beans调用换为不演剥豆的注释；217–218行3.8s rustle、4.0s burst原样保留，S01豆声未改。

未收到作者声明的新母带SHA256 `6980b2ffd039ca4189fdac15ca71c36a7422a61a56bee9454ad8714490de9ede`：主仓build/audio/film_mix_norm.wav不存在；独立worktree同名文件可读但仍为旧SHA256 `6980ce06f50f6348b8f832d23cfb4a5d72edddda61ab47ade274727ecaaf18c4`，47136078 bytes。

因此−16 LUFS/−4.4dBTP/LRA8.2及后段约±3%动态增益变化目前均是作者报告，未独立复测新版。只关闭S03多轮豆声的源码项；待新母带实际交付或新片音轨再核。不重建母带代替交付、不拿旧WAV冒充新文件，批1图与曝光制作继续。
