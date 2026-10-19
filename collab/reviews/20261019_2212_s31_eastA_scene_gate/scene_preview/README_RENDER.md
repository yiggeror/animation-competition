# S31 A exact-source scene candidate, three scene frames only

Prepared 2026-10-19. NOT rendered yet: local Chromium launch was blocked by `socket() failed: Operation not permitted`. Do not treat this entry as a reviewed production scene.

Run from `/workspace/scratch/f060b5601755/s31_first_inputs_20261019`:

`NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node scene_preview/render_keyframes.cjs`

The runner starts and closes its own temporary localhost HTTP server. The runner uses installed `/usr/bin/chromium` and Playwright. It writes only two 960×540 A candidates (F000/F116), original B F180 before and after A, registration JSON, and exact A→B pixel-difference JSON. It does not write repository assets or full video.

`preview.html` is also the browser entry. `window.ready` signals loaded references. `captureBReference()` captures original B frame180, `renderFrame(f)` renders one A test, and `checkBAfterA()` repeats that exact original B frame with exact channel differences. B is called only at original time7.5 seconds.

## Fixed sources and isolation

`SOURCE_LOCK.json` records all 18 exact original modules at44883e8c502a6066a33c67be0e58cf7185554759. Original `js/lamp/s06_key.js`, S31 B, shader, lamp values, and timings remain byte-identical. A-exclusive `s06_key_s31a.js` changes only the approved right quilt edge2.368→2.85 and grandma blocker centre[1.05,.88]→[2.90,.28]; A owns a separate module GL instance/cache. Original B uses its original module and camera.

A background camera uses approved east target[1.60,0,.86], position[.82,-2.05,.78], hfov52. Foreground matrix/329.16px head width is locked. Background backdrop alone retains original low-resolution render and14px defocus. A backdrop has original pond/willow only, since turtle is now in the child's hands and the crane is physically in the bundle.

## References, no copying

- F000_final_mother/S31_F000_MOTHER.png
- F036_expression_call01/S31_F036_CHARACTER.png
- F116_lift_call01/S31_F116_CHARACTER.png
- background_east_inputs/s28_gm_F000_SOURCE.png
- BUNDLE_halfopen_call01/S31_HALF_OPEN_BUNDLE_WITH_ORIGINAL_CRANE.png
- background_east_inputs/S31_EAST_A_PROJECTION.json

The generated bundle is layered with the original complete folded crane parts inside its real cavity. All native cloth lips and dark cavity remain opaque; original parts are hidden by the native lips. Ground and mouth are registered to the same physical bundle, with ground[2.86,.30,.02], mouth[2.86,.30,.32]. Bottom is below this camera's crop, not floating. Grandma uses the approved original S28 pose and scale; she stands beside the floor bundle, not holding it unsupported.

## Review needed

Actual engine visibility/occlusion of grandma and bundle; mouth must stay above crop and legible after original defocus. Code lamp must naturally illuminate underside of face with actual fixed lens/axis, no baked identity recolour. True shell/head rods use both actual hand-entry positions and constant lengths. Foreground remains unmodified drawings. This is a few-frame integration candidate, not approval of the remaining116–163 wrist-led animation group.
