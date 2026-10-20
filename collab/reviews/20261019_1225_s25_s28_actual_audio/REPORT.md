# S25 / S28 actual audio delivery check

Fixed delivery: 582bd1b6b89bfc52b58143ab76a778750ea987cd. Both new sound clips preserve the approved silent H.264 stream byte for byte. This is signal/container and fixed-source verification, not subjective listening.

The normalized independent master from fixed 571cf92 is reused only after all five audio/package sources are rechecked byte-identical and the complete ordered EDL id/duration list is equal. Module-path changes do not affect build.py, which reads only id and dur.

## S25
144 frames / 24/1 fps / 6.000000 s. 288000 stereo PCM samples at 48 kHz.
MP4 SHA256 8cdb847790ac573e84fa43c7c022e3160f09c9860865e4ba1b64d99681a0e50b
PCM SHA256 76f5719508dbf549c9a4fcf980cb31d09f6e1bbf2430bbe68b04327b75935464
H264 matches approved silent source: True. PCM to master max 2.0 LSB, RMSE 0.01094494 LSB. AAC best offset 0 samples, correlation 0.999116005, true peak -4.49 dBTP.
EDL module: js/anim/s25_drawn.js.
Event-window sample checks: [{"time": 1.2, "frame_at_24fps": 28.799999999999997, "sample": 57600, "window_max_lsb": 0.0, "window_rmse_lsb": 0.0}, {"time": 4.6, "frame_at_24fps": 110.39999999999999, "sample": 220800, "window_max_lsb": 1.0, "window_rmse_lsb": 0.007216878364870323}, {"time": 5.35, "frame_at_24fps": 128.39999999999998, "sample": 256800, "window_max_lsb": 2.0, "window_rmse_lsb": 0.013501543121683042}]

## S28
192 frames / 24/1 fps / 8.000000 s. 384000 stereo PCM samples at 48 kHz.
MP4 SHA256 1240b0bc4dd8747bb3a88cb464273540f39ce02ea5bdb910c7c2f1ec0823c85b
PCM SHA256 941ff967981777eda1e8a69f76b7ca8ea49c42dc684f2f47a68f980ffb2f65a1
H264 matches approved silent source: True. PCM to master max 2.0 LSB, RMSE 0.00988212 LSB. AAC best offset 0 samples, correlation 0.999571732, true peak -4.43 dBTP.
EDL module: js/paint/shots/s28.js.
Event-window sample checks: [{"time": 0.2, "frame_at_24fps": 4.800000000000001, "sample": 9600, "window_max_lsb": 1.0, "window_rmse_lsb": 0.005103103630798288}, {"time": 1.4, "frame_at_24fps": 33.599999999999994, "sample": 67200, "window_max_lsb": 0.0, "window_rmse_lsb": 0.0}, {"time": 5.5, "frame_at_24fps": 132.0, "sample": 264000, "window_max_lsb": 1.0, "window_rmse_lsb": 0.008838834764831844}]

