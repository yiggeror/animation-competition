# S07 090×5 → 095×5 原机位实际10帧

依Astra主／独审锁定的原色090 `012e7bae…` 与095 `dcf919f4…`，只做场景090–099：24fps、1280×720、10帧、无补间／音频。原整图注册和原机位裁切完全沿前一已交曝光；没有校色、新生图或100曝光。

[灰底实际10f](exposure/gray/S07_F090x5_F095x5_gray_actual_24fps.mp4)／[灰底指定实解码0、4、5、6、9](exposure/gray/actual_decoded_contact_sheet.png)；[深底实际10f](exposure/dark/S07_F090x5_F095x5_dark_actual_24fps.mp4)／[深底指定实解码](exposure/dark/actual_decoded_contact_sheet.png)。两底目录另保留原尺寸指定帧和腿脚2倍查看图；[全部20帧解码记录](exposure/actual_decode_checks.json)。

root已实际看两底全部指定帧及4→5腿脚放大：近右后脚由090步幅收齐至095前景落稳，远左原支撑鞋留在原位并自然被前鞋／裤遮挡，腰臀双腿随同已锁姿态回稳。地线保持，未见鞋滑到新地线、独立鞋缩放或明确裤色闪变。095原色按主／独审锁定保留。全部20解码帧均最近匹配正确源态，灰／深最大RGB编码MAE约0.235／1.160以内。

结论：此独立10f曝光检查已完成，交Astra审4→5实际落稳与相邻节奏；不代完整108f／全片通过。100仅准备输入、未调用。S09另按独立权限处理，不混入此曝光。

两张源PNG与原提交逐字节同；最新锁定原话、原配准和源SHA在sources。`python verify_delivery.py`只读复核来源git字节、包SHA、ffprobe和每一个实解码帧；`build_exposure.py`可重建。此次曝光零图像调用，原画全prompt／原件／返回仍在对应090／095原调用包。
