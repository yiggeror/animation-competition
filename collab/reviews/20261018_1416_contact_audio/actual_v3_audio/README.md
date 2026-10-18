# New S03a/S05a v3 encoded media incremental review

Actual latest clips: `collab/reviews/20261018_opening_drawn_wip/S03a_drawn_v3.mp4` at 3f4e9cea66d56ef897e1d84669a71232d4cc80f4; `S05a_drawn_v3.mp4` at 18112f36e40ab7cf24fa9870f8e0c725069a8aad. Both remain present in 18112f36. Source commits and SHA256/bytes in respective JSON.

Both elementary H264 streams are byte-identical to their already independently visually reviewed actual Canvas render, 36/60 frames. No reason to repeat identical frames. New AAC was actually decoded: 48 kHz stereo, best lag 0, correlation 0.998826 / 0.999483 to the matching PCM, peaks -5.13/-5.42 dBFS. AAC padding beyond 72000/120000 content samples is explicit, not extra shot duration. AAC is lossy; not byte-identical PCM.

PCM blobs match the previously independently rebuilt-and-checked slices exactly. All four audio Python source blobs match the latest 18112f36 tree, and actual EDL changes only switch drawn module references, not durations. Thus prior 3/2 LSB rebuild residual remains relevant; no stale original beans/master conclusion reused. Two press events remain 39/24 and 44/24 within S05a.

This closes new mux content/timing and previously reviewed visual continuity. It is not a subjective original-speed naturalness verdict or proof that Opus has actually sent either version to the user. Opus's claude selfreport says accepted/muxed, with no verified user-send record here.
