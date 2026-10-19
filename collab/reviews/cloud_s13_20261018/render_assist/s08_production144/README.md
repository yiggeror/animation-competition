# S08 production144 thin equivalence handoff

Production source `54796bf3835d6fe8e32a78ea3c854ac2a5d34d15`, entry `js/anim/s08_drawn.js`. The approved command was run once: `node tools/js/frames.cjs js/anim/s08_drawn.js build/S08_production144 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_production144.mp4` (read-only browser/network audit preloaded).

All144 actual production Canvas PNGs are byte-identical to approved candidate `dd6e23bca9f06bf219d2aff81d5aeab44f03c4ab`. The production MP4 is also byte-identical: SHA256 `e3f4fc04364d46ec7ff690ef7c20b2dd3138ce70219f75e3e173af87262d65be`. 144f /6s /1920×1080 /24fps /silent. Candidate was not rerendered. The previous complete decode proof applies by identical MP4 bytes; four production keys 000/096/136/143 were independently decoded for the included preview.

Actual browser audit:112 unique production PNG assets, all HTTP200; reviews requests0; page errors/failed requests0. The incidental favicon404 and console location are retained in the audit. No imagegen, shared ready, EDL or audio edits. Astra can register ready and hand to Opus for sound.

Thin package contains MP4, actual production decode preview, all144 byte-comparison ledger, actual network log and summary. Full raw production Canvas files remain in the local build cache; they are not duplicated in Git.
