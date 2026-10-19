# S30 complete 288-frame module candidate

22 locked, byte-identical whole-character originals. One wholebody similarity per pose. No segmented human renderer and no interpolated sliding actor. This is a scratch candidate for coordinator review, not a repository write or final export.

- `s30_drawn.js` → `js/paint/shots/s30_drawn.js`
- `RAW_ASSET_REUSE_SHA.json`: each exact original path/SHA and intended repository asset path. Coordinator copies the original bytes; no image conversion.
- `S30_LOCKED_ORIGINALS_AND_COMPLETE_288F_BINDING.json` is in the parent directory and contains the full source/request/matrix/exposure table.
- Source helpers remain unchanged: `js/paint/paintshot.js` and `js/paint/shots/s29_lamp.js`. No EDL change in this package.

## Timing and layers

24fps, 288 frames, 12 seconds. TV switch event1.1s/first sampleF027 uses original CRT collapse behavior; first south frameF040 follows exact1.65s cut. Six footfalls remain036/048/060/072/084/096. F132 exactly reuses final120. F138/F143 original same beige knob and rope endpoint hold with their respective complete-hand poses. F144 independently turns the room light off. F147 opens the hand and starts the original-style damped recoil from the actual last-held knob location. F190 is first sample of the untouched7.9s `renderFrozenHead` branch, through287.

The left flashlight lens and barrel tail are annotated on each actual pose and transformed by that pose's one wholebody matrix. Its light stays on, including after144. Emissive lens and directional light are scene layers only. Soft shoe contact shadows follow actual sole-bottom alpha contours for planted poses; passing poses receive only a small contact mark at the locked support toe. No shoe is moved to fit a shadow.

## Checks completed here

- `ALL_288_STATE_ASSERTIONS.json`: full288 sample table/event/camera/held-prop/recoil-origin assertions,22 original SHA checks. This is state logic, not a full scene visual pass.
- `CPU_F*.jpg`:15 keyframes rendered by unchanged44883e8 production `renderPaint` under a no-socket `@napi-rs/canvas` compatibility shim. These are CPU previews, not Chromium/WebGL final output.
- `CPU_KEYFRAME_STATES.json`: exact sampled states and renderer disclosure.
- Local Chromium could not start. Both real error receipts are in `BROWSER_ENVIRONMENT_BLOCK_RECEIPTS.json`. No more local browser attempts; no restricted directory accessed or changed.
- Original shadow branch190–287 was not rendered locally. It must be run in the existing original cloud repository with its original four `g29_prepare_blow` assets and WebGL support.

## Minimal original-cloud render

After the coordinator installs `s30_drawn.js` and the manifest's original assets, preserve this folder's `render_repository_keyframes.cjs` and `RAW_ASSET_REUSE_SHA.json` together under `collab/reviews/20261019_2226_s30_complete_scene_gate/`. From the repository root:

`node collab/reviews/20261019_2226_s30_complete_scene_gate/render_repository_keyframes.cjs`

This verifies all22 installed raw SHAs and renders20 keyframes including190/287, with an actual browser error/missing-asset report. No shared module or EDL is modified.

For the final silent288-frame candidate after the keyframe gate:

`node collab/reviews/20261019_2226_s30_complete_scene_gate/render_repository_keyframes.cjs --all`

This pipes encoded frames into ffmpeg and does not create a PNG frame run. Audio remains the existing approved sound track, to be joined by the coordinator. A rendered result is still subject to actual scene/continuity review.

## Portable entry and state isolation audit

`PORTABLE_ENTRY_AND_ORIGINAL_TAIL_AUDIT.json` resolves both direct imports and the 16-file unchanged helper import closure against original commit44883e8c502a6066a33c67be0e58cf7185554759. All22 raw URLs match the installed asset manifest. The original room background and four original grandmother map/mask files have exact pre-existing SHA/blob provenance in the manifest; they are reused, not copied by this package.

`CPU_RANDOM_ACCESS_ISOLATION.json` records10 actual CPU renders at480x270 in scrambled north/south/light-on/blackout/release order. Each of five repeated frames has identical decoded RGBA SHA. This is CPU renderer isolation only. The original-cloud script additionally checks120→190→000→190→120 encoded-frame hashes against the first render in the same actual browser, without appending diagnostic frames to the output.

The cloud script validates the22 raw assets, two unchanged direct helpers and five existing background/shadow assets before launching. It records failures inACTUAL_BROWSER_RENDER_REPORT.json, ignores the irrelevant favicon request, and usesCHROMIUM_PATH when supplied (otherwise installed/usr/bin/chromium or the existing Playwright browser). No browser download or installation is performed.

The current gate runs only the default20 saved keyframes plus five unsaved isolation rerenders. Do not run--all until the coordinator passes this actual browser gate. The script is directory-independent: it uses__dirname for its manifest/output andprocess.cwd() for the original repository. The expected preview URL ishttp://127.0.0.1:<allocated-port>/__s30_preview.html; the exact allocated preview/module URLs are saved in the report. Favicon requests are answered204 and logged separately. All actual HTTP/request/page failures are recorded independently.
