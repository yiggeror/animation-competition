# Opening corrected actual full shots — all three clips archived

Fixed production source `c57538925035118c0f8901fc2f22f478fbf803b4`. S01 (84f) and S04 (72f) remain the original completed deliveries, byte-exact video hashes unchanged. After the original three-scene run failed at S07 F008, main coordination independently reviewed the evidence and authorized exactly one S07-only fresh-page continuation. That continuation completed F000–F107, exit0, using unchanged Chromium flags and default Canvas attributes (`willReadFrequently:false`), with no prior S01/S04 render calls on the page.

S07 actual MP4: `S07/S07_opening_corrected_1080p24.mp4`; SHA256 `c1c282946ec0a4b4a20bdf5d0f5ba76d8ceb2e04df616faa7271dd9d3317e421`. It is 108frames, 1920×1080, 24fps, 4.5seconds, no audio. All five original S07 approved PNG gates F008/F039/F043/F053/F057 passed byte-exact. Combined with retained S01/S04, all seven approved sample gates now pass; see `FINAL_THREE_DELIVERY_CHECK.json`.

S07 native key PNGs, all108 native PNG SHA rows, independent ffprobe and complete108-frame RGB24 decode hashes, plus decoded focus/contact sheets are in `S07/`. Root actually opened the decoded sheets for throwing F000/003/006/008, F038/039, F053/056/057 and tail F099/100/103/106/107. These keys remain readable; main coordination retains full continuous visual review and audio/EDL decisions.

Single continuation renderer node PID74750 exited0. Before/after frozen source checks, 57 successful HTTP responses, empty request/page error list and exit records are in `S07_FRESH_CONTINUATION_c5753892_20261019/`. Its producer and independent verifier are archived there. No production source/art asset changed, no S01/S04 rerender, no new image generation.

Historical evidence is preserved unchanged: the original `RUN_STATE.json`, `FULL_THREE_CHECK.json`, `PUBLICATION_STATE.json` record the first failed run, not this continuation. `FAILED_S07_F008_DIAGNOSTIC/` retains the original failed/approved PNGs and 51 matching dependencies; `S07_CONTEXT_HISTORY_DIAGNOSTIC/` retains earlier finite fresh-page results. The precise earlier cross-scene execution mechanism remains unproven and no tolerance was relaxed.
