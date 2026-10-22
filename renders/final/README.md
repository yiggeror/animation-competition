# 《奶奶的皮影》成片

`nainai-de-piying_1080p24.mp4`：1920×1080，24 fps，5883 帧，245.125 秒（4 分 05 秒），H.264 High + AAC 256k 立体声 48 kHz；
响度 -16.1 LUFS，真峰 -1.9 dBTP（编码后实测）。

仓库里按原字节分成两段（GitHub 单文件上限 100 MB）。还原：在本目录运行 `python3 restore_final.py`，脚本会核对字节数 116326266 和 SHA256 `45b03097a2e62baf6f88c2f79f4b4cde05753101db63363918a80b25e7e8b6b4``43fac77450d315cfee22ce71e42f3140e58d051caf8a32d82d3224422b2fb949`。

重新生成：`node tools/render_film.mjs` → `python3 audio/build.py` → `node tools/master_film.mjs`（见仓库 README"成片怎么做出来"）。
