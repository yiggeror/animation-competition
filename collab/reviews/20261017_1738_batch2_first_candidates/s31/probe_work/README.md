# S31 回舌两态 · 24帧试接包

**只供Opus独立试接，不是S31正式336帧表，未启用、未渲片，也未宣称原速/光照/手灯合成通过。** 本机隔离目录运行既有prep与manifest，仓库未写入。两态六张三图全部1024×1536；24帧表、尺寸、配准范围、原件身份、alpha公式与三图alpha一致性检查均exit 0。

## 使用与复制
包内 `assets/chars/` 六张PNG分别复制到仓库相同相对路径：
- `assets/chars/x31_mouth_probe_k01.png`
- `assets/chars/x31_mouth_probe_k01_n.png`
- `assets/chars/x31_mouth_probe_k01_m.png`
- `assets/chars/x31_mouth_probe_k02.png`
- `assets/chars/x31_mouth_probe_k02_n.png`
- `assets/chars/x31_mouth_probe_k02_m.png`

`assets/flips/x31_mouth_probe.flip.json` 仅复制为同名诊断表，不覆盖任何正式S31表。完整源→目标相对清单见 `COPY_PATHS.json`。表为24fps，F0–5旧嘴、F6–17闭嘴、F18–23旧嘴。原件另留 `collab/refs/x31_mouth_probe_k01.png` 与 `k02.png`，哈希保持不变：母图 `0eda0496336ff1128474680389d8c55b36e6eb54d6d6584ce695f399e22e5cbc`；唯一新原件 `a733a8eccdc8aa42cf54761b31bf5ca3594370c1958067c5b3d11f6cba1e893f`。

## 规范处理与测量限制
prep直接保留RGBA，alpha按 round(clip((A−6)/(247−6),0,1)×255) 标准化；RGB逐字节未变，没有重抠灰底、裁画幅、贴回母身或几何校正烘焙。k02原alpha最大254，处理后内部恢复255。两态的固有色/法线/材质尺寸与alpha逐像素一致。见 `validation.json`、`prep.log`、`flip_manifest_24.json`。

固定A=(272,1187)、B=(630,1176)、独立H=(530,873)。旧NCC在长斜裙褶上误取B=(630,1173)，其拟合后H3.403及手漂移不能当真实形变结论。原始自动报告保留在 `review/candidate_measurement.json`。同一冻结白点/黑线特征经人工及协调独审复核，k02采用B=(631,1176)，没有换点或用H拟合；手工M后H1.131px、右拳1.621px、左掌1.699px。B±1px单独传播，H最坏2.257px；右拳/左掌最坏3.233/3.968px，因此试接仍须核实际手灯/签遮挡，不能承诺所有固定点误差上界都≤3。两套方法和独审在 `review/manual_same_feature_check.json`、`review/coordinator_B_feature_check.json`。

## 同一M换算掌签点
每态fields是原图像素，必须和图像使用同一Canvas M，再由场景变换一次。
- k01：M恒等；grip=(850,607)，tip=(942,470)，换算后同值。
- k02：M=[0.9972170974093425, −0.0000852699958140195, 0.0000852699958140195, 0.9972170974093425, 0.6557340196275732, 3.3264988139719662]。
  - 原grip=(851,607) → 母版(849.3392428024,608.5647121750)
  - 原tip=(942,469) → 母版(940.0742314073,470.9409931629)
掌心是被手指遮住的杆轴在掌内的投影，tip是可见签上端轴心，手工点位约±3px。旧s31.js的(880,548)是出签/拇指附近，不能替代掌心。程序龟/杆必须跟新轴，避免旧原画签与独立wig杆岔开。固定源码尚未接此点位接口；本包不修改它。

灯/手指仍按既有FL、FIST、去灰ROI和筒尾补衣料接口试接；须先统一到母版坐标，核灯头/下巴间隙及前景手指。未恢复0714奶奶退出WIP、未改F180后皮影、未加click或改F24笛子。

复现命令仅在包根目录执行：
`python3 -I tools/prep_flip.py collab/refs/x31_mouth_probe_k01.png collab/refs/x31_mouth_probe_k02.png`
`python3 -I tools/flip_manifest.py x31_mouth_probe 24`

工具快照及原件哈希见 `source_and_tools_manifest.json`；所有交付文件哈希见 `delivery_manifest.json`。没有调用新生成。
