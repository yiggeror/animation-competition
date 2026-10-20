# S30 adopted sound clip: fixed actual incremental check

Fixed delivery428d40d1a73ccbda9111324965e7ceec4cb00a1d. The MP4 and PCM match its manifest. All288 approved silent H.264 frames are preserved byte for byte. Video/AAC presentation duration12.000s,1920×1080,24fps; PCM48kHz stereo576000 samples. AAC preroll1024 samples is signaled; final packet duration512 samples and12s presentation are consistent.

The six fixed source files were retrieved unchanged and audio/build.py actually executed independently. The new normalized master SHA256 is 0f5380057fb73100b1cc03057223a4a0d8022bdd6da06652dcd70ec30f7fbf51. Delivered PCM matches master samples8740000–9316000 with maximum3LSB and RMSE0.01074483LSB. Event windows around actual F027/1.125s and F144/6.000s each differ by at most2LSB. The new build truly usesTV_OFF=27/24 andOFF=144/24; the former old1.1s setting was not reused.

AAC best offset0 samples, correlation0.999484082; measured true peak-4.49dBTP, integrated loudness-19.76LUFS for this12s excerpt. EDL selectsjs/paint/shots/s30_drawn.js. This verifies actual signal/container/events against a fixed-source independent rebuild; it is not subjective listening and no Opus-machine master was obtained.

MP4 SHA256df47e3f2edb64bef7246c1b85b38f2ae04d15944bd76719ae321284ff46a8e14
PCM SHA256ab815b20dc242b02ae5b0b9a9ca42ad529b05eaf2bf71471887a6b26ce354c5c
Approved-video H264 SHA2562e67feeaef7c29e88916c2a532bd0f75cc069e622fa033d574896ccc8f0f03e2
