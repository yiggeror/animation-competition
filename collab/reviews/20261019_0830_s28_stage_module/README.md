# S28 stage module candidate (000–131 only)

Install this directory verbatim at `collab/reviews/20261019_0830_s28_stage_module/`.
No 25 locked PNGs are duplicated. Runtime reads their existing sibling directory at fixed asset commit `8065837662b3c1252d82a0bf75e9837ac12523dd`.

## Run the required three frames from repository root

Prerequisites: existing Chromium and Playwright, existing repository `js/` host scene. No install or generation is invoked.

```sh
python3 -m http.server 8194 --bind 127.0.0.1 > /tmp/s28-stage-http.log 2>&1 &
S28_HTTP_PID=$!
mkdir -p /tmp/s28-stage-three
S28_OUTPUT_DIR=/tmp/s28-stage-three node collab/reviews/20261019_0830_s28_stage_module/render_three.cjs
S28_STATUS=$?
kill "$S28_HTTP_PID"
exit "$S28_STATUS"
```

This emits `F000_png.png`, `F012_png.png`, `F042_png.png`, matching foreground/shadow diagnostics, and `RENDER_SELF_CHECK.json`. The three `_png.png` files are the full-scene candidates. Optional `CHROMIUM_PATH` and `S28_PREVIEW_URL` override those exact executable/URL defaults. Run serially; do not share mutable host `S` with concurrent shots.

## Entry and dependencies

`preview.html` → `preview.mjs` is the exclusive review entry. Host imports resolve to `../../../js/...`; artwork comes from `../20261019_0820_s28_locked_stage_assets/FRAME_BINDINGS.json`. Its `source` values resolve against repository root, not the assets directory. Local five masks and joint bindings come from `./local/`.

`createS28StageCandidate` supports `options.bindings` (object or URL), `bindingsFile`, `assetsRoot`, `repoRoot`, `localRoot`, and an optional `resolveSource(row)`. Original local `asset` table and production `source` table normalize to the same frame/SHA selection. `renderFrame(ctx, seconds, W, H)` requires frozen 16:9 HFOV94 camera. Phone frame132+ throws; it is not silently held or invented.

Host dependencies injected into the factory: `renderShot`, `sceneState`, `drawPuppet`, `sheetAtEnd`; optional `extraLayers` supplies the existing lamp. `freezeS27End` uses the original S26 endpoint solver/pose with S27 end offsets. All four original puppet endpoint checks are exactly zero in the CPU test.

## Depth and shadows

Real full-body RGBA is uniformly registered once. Float64 local ray-distance ordering resolves actual people, four 3mm-radius straight rods, original puppets and lamp before delivering Cards alb/nrm/mat maps. XM033 depth eases0→1 into036;045 eases1→0 at048. The five complete real RIGHT-arm masks preserve original RGB and silhouette; shoulder stays fixed, elbow−60mm and wrist/hand−100mm. No continuous actual-motion collision proof is claimed.

GM actual RIGHT shoulder/elbow/wrist depths are1.933369/2.099548/2.322202m, with continuous sleeve→elbow→wrist→palm field reaching the exact2.353682/2.359464m contacts. Upper/forearm255.8/263.2mm; hidden joint picks±20rawpx. Four contact error≤2.5e−16m. Wrist cross-section jump across2e−5rawpx is8.5e−9m. This is a feasible depth surface, not recovered anatomy. GM006/012 use the same small-motion guide and remain a visual-review caveat.

Contact shadow source is cropped lower-leg/shoe alpha of real characters only. No rod/puppet alpha enters its source. Old host `S.occ`/`S.occBack` proxy shadows are suppressed only during this render and restored in `finally`. The receiving Cards depth remains8bit (31.37mm per step), so external large-scene occlusion is not newly proven. Ground-shadow placement and final lighting must be judged on the three full scenes.

## Actual validation status

PASS: syntax; all264 character/frame selections;25 actual source SHA; four real contacts; three real joint depths; continuous wrist field; entry/exit envelope; frame132 rejection; CPU local composition of F000/012/042 including original puppets and four rods (zero puppet-endpoint drift).

NOT EXECUTED: full host WebGL three-scene render. Local Chromium socket access was blocked; elevated executor failed before launch. No final scene image is claimed in this package. Use the existing authorized cloud render environment and review all three together. CPU diagnostics are not substitutes for that gate.
