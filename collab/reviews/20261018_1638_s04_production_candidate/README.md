# S04 production-path candidate, complete72frames

Ready for the coordinator to publish the seven files listed in `PUBLISH_FILES.txt`, then render the actual full72-frame scene directly at the production path. No repository file has been written by this task. No image generation was used by this module preparation. Real Canvas lighting/contact/sequence approval remains pending.

## Publish and render

Entry: `js/anim/s04_drawn.js`
Dedicated timing helper: `js/anim/s04_drawn_timeline.js`
Five exact approved PNGs: `assets/chars/s04/`

`PATH_MAPPING.json` gives every production path, source, full SHA256, dimensions, exposure and already-registered world mapping. `DEPENDENCIES.json` records unchanged original renderer/prop/core/tool blobs rechecked at16:36UTC. All runtime modules use.js.

```sh
node tools/js/frames.cjs /js/anim/s04_drawn.js build/s04_drawn72 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 3 --mp4 build/S04_drawn72.mp4
```

Render0–71 inclusive, exactly72frames at24fps. Export actual MP4, log and decoded F000/006/007/008/021/022/027/028/033/034/071 for the blackout and head-state transitions. Do not alter EDL/audio/legacy scene helpers when publishing these files. Local package/test/provenance files are QA evidence and are not additional root runtime dependencies.

## Frozen timing and pixels

- G0–6 and7–21: exact S01G012, first split pod with2nested beans.
- G22–27: final6fc727833e49c9e0e70f9bb67d5755352b2a38b453b3678d60816ee2f41ad377.
- G28–33: finale08c927ad58a481a9cf2d3c8ec790efdf94ba0e7e080e2549673d5282c76b468.
- G34–71: final32cada22cb7094e0539913ed591bf54d4b61a2ed8c017c4cf812316849f67b43.
- X0–71: accepted S01F010/F035 low-leg pixels04696fecfc23579ebc336220a0d5d60cfeae24de73d73e105526db929f98d11c.

G uses world(.2734375×asset)+(730,375); X uses(.16×asset)+(399.28,533). All PNGs are already registered. Do not apply raw-to-canvas again. G images each contain the single basin; do not add another basin. Each of22/28/34 was additionally checked to have exact G012 RGBA from asset row735 through the bottom, including static hands/pod/beans/basin/legs.

## Only path migration in this package

Compared with the completed isolated S04 candidate, the source changes are exactly two literals:
- `./timeline.js` becomes `./s04_drawn_timeline.js`.
- `./frames/` becomes `/assets/chars/s04/`.

After reversing those replacements the JS is byte-identical. Timeline is byte-identical. All five PNGs are byte-identical. Camera, timing, light and all scene behavior therefore remain the accepted candidate definitions; no new visual changes were folded into this move.

## Scene-review checks

One blackout at7/24:7bright frames,65dark frames. Light, TV-collapse and fan deceleration use that same cut. Original S04 camera stays(816,482.5),fit1.04, with original background/lamp/matchbox/stool/coil/moon-shaft/TV-collapse/fan behavior.

Previously approved S04 corrections remain: actual X010 phone-region anchor(651.5470,623.1512), with approximately2scene-pixel measurement uncertainty, replaces obsolete code anchor. Original point-light parameters and y−6offset are retained. Source r14 blue halo is scene-only and alpha-occluded by the complete X010 silhouette so its opaque phone back/fingers are not painted as a screen. Actual cloud lighting still needs inspection; hidden screen tapping is not claimed.

Three final head drawings have static approval. The actual72-frame original exposure, blackout beat, gaze/neck transition and final38-frame hold still need playback review. No isolated placeholder frame or code-painted person is used.

Local check:

```sh
node --input-type=module --check < js/anim/s04_drawn.js
node --input-type=module -e "import('./test_production_contract.mjs')"
```

`checks/TEST_RESULT.json` verifies all72 selections, zero missing assets, cut7, dimensions/SHA, path-only migration and unchanged timeline. It is not a Canvas render.
