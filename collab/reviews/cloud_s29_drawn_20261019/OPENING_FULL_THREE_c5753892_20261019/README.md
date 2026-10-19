# Opening corrected actual full shots

Fixed source c57538925035118c0f8901fc2f22f478fbf803b4. The original streaming render exited 1 at S07 F008; no full renderer was restarted. Each completed shot was archived and independently decoded before its own publication.

Completed: S01 (84f, commit 70d3bb7b0db4b3e6193abfd049a82c336af3626e), S04 (72f, commit 89708c465f87698c2fce2fbec339b18e0ef20338). Video, original key PNGs, all frame hashes, CLIP_CHECK and independent decode checks are in each shot directory. Both are 1920×1080, 24fps, silent. The corresponding approved samples passed byte-exact checks. Full continuous visual review and audio/EDL remain with main coordination.

S07 is HOLD, with no valid full108 clip delivered. `FAILED_S07_F008_DIAGNOSTIC/` preserves the original failed PNG, approved PNG, actual visual difference and all 51 fetched dependency comparisons. The difference affects 662,702 pixels with maximum channel delta 3; the strict gate remains unchanged. Original runtime final reports and exit state are archived at this root; no original HTTP/page errors or frozen-source differences were found.

`S07_CONTEXT_HISTORY_DIAGNOSTIC/` (commit 47ceb850f3057c9761e84fd3948e9059713aef09) adds finite S07-only checks: fresh direct F008, fresh sequential F000–F008, and fresh direct F008 with readback-friendly context all reproduced the approved F008 exactly. The mechanism behind the original preceding-execution difference remains unproven. These checks neither rerendered S01/S04 nor produced/replaced a full S07 clip.

Original node 70767 and HTTP 70765 have exited. No full-shot renderer remains active. Further S07-only execution can preserve completed S01/S04, frozen source and all five strict S07 approved sample gates; this package does not authorize a relaxed comparison.
