# S08 full144 actual render handoff

Fixed source: `6ef3b0b03c1f800193df1018bd7f1af51a3bd6f0` (121 supplied paths). Entry: `collab/reviews/20261019_0443_s08_full144_scene/s08_full144_candidate.js`.

Delivered `S08_full144_1920x1080_24fps.mp4`: 144 frames, 6 seconds, 1920×1080, 24fps, silent. MP4 SHA256: `e3f4fc04364d46ec7ff690ef7c20b2dd3138ce70219f75e3e173af87262d65be`.

Only new frames 096–143 were rendered once. The approved corrected-shadow 000–095 Canvas cache is reused byte for byte from first96 delivery `23c5b5f1a2389c99ca73010827c8b22371b18c7a`; the obsolete pre-shadow cache was not used. New 48 Canvas PNGs and 13 actual decoded keys are included. No 144+ frames or image generation calls.

All 144 source/decode comparisons passed (maximum RGB MSE 10.157303). Actual network audit records all 24 new layer files over two workers as HTTP 200, no page errors or failed requests. The old96 code subsamples, metadata, layer bytes, shared runtime, and match-shadow contact inheritance were checked before capture.

Actual decoded boards were inspected: 095→096, 105→106, 113→114, 121→122, 127→128, 135→136, and 143. Hands, one box, fixed discarded match/contact shadow, wick/smoke area remain readable; 136 settles head/neck/chest together. See `visual_review.json`. This is the author handoff for Astra’s final review; shared ready/EDL/audio were not edited.

Reproducible capture/assembly and provenance: `tools/`, `assembly_commands.json`, `actual_network_events.jsonl`, `reused96_baseline.json`, `static_old96_parity.json`, `fixed121_readback.json`, `all144_source_decode_checks.json`. All changes are inside this delivery directory on the private branch.
