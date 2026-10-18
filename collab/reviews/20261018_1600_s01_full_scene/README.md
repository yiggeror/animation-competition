# S01 complete84-frame drawn-scene candidate

Frozen2026-10-18 15:59UTC. All18 character PNGs are finally accepted and present; all84 frame positions and every PNG SHA/dimension pass. Full original Canvas scene visual/timing review is pending. This is a local collab candidate, not a production/EDL/audio/shared-helper change.

## Entry and files

`s01_drawn_candidate.js`: renderFrame/render, DURATION3.5, FRAME_COUNT84,24fps.
`timeline.js`: all19 character exposure keys across14 grandma and5 Xiaoman keys, with4 unique Xiaoman PNGs and14 grandma PNGs.
`frames/`:18 exact final RGBA PNGs. `ASSETS.json`: source paths, fullSHA, registered dimensions and scene mapping. `DEPENDENCIES.json`: repository dependencies and their read blob identities. `TEST_RESULT.json`: complete84f test, no missing ranges. `SHA256SUMS`: every delivered file.

Serve this folder intact anywhere beneath the original repository HTTP root. Absolute imports `/js/paint/paintshot.js`, `/js/paint/shots/s01.js` and `/js/code/s08.js` refer to existing renderer/props; frame URLs resolve relative to this module. No complete-scene image has been rendered in this package. Prior partial-probe/test history remains outside this frozen package in the author's working provenance directory.

## Fixed registrations

Native plate1672×941. G1024×1536 uses scale.2734375,translation(730,375). X1792×1024 uses scale.16,translation(399.28,533). Every PNG is already registered; never reapply raw_to_canvas. No extra flip, crop, character rotation or body deformation is applied in the scene.

Grandma assets contain the basin/beans/hands. Xiaoman assets contain both hands and phone. No duplicate basin, beans, code person or code phone. Original stool is separately drawn with original primitive and charLayer pre-transform. Background, table lamp/matchbox, coil, fan, TV light, smoke, lighting and camera follow original js/anim/s01.js. Light/glow/emit/camera block is byte-identical to that source. Missing assets/background or changed canvas dimensions throw; no placeholders.

## Exact original exposure

G:0000–9;01010–11;01212–27;028–034one frame each;03535–49;05050–61;06262–69;07070–83.
X:0000–9;01010–19;02020–34;035uses01035–42;04343–83.

X043 final41frames hold prone-playing; they do not show continuing kicks or visible screen-thumb taps. X static states and independently decoded84f isolated original exposure have passed. Whole-scene timing remains for actual Canvas review.

Grandma035 is corrected alpha final9c990585a527f2d61f994f73b9e727949cb0aecfe6a260bff19fe1381d9925d6.
050 final40576c390567a2ccf9bf7af81aeb14080daaf283e4d54e18decc1fbe8fc49303.
062 final187d94855ad8aa73b71d8da9fffaa8681ce5eddb94cbb54ce57151a923c31a7c.
070 finalab4744921b19448283aff27ea729ea6d2ba4b3b90dbc0d1247b981567a055eb8.
All other fullSHA values are inASSETS.json.

## Cloud review

Render all84 real Canvas frames at24fps with the original scene. Check stool-seat contact, feet and elbows on original floor, correct single registration, single basin, grips/beans, near/far leg switch and unchanged camera/light/props. Do not substitute a PIL collage or claim neutral character preview is original-scene evidence. Parent coordination owns cloud rendering and repository publication.

Runtime module files use .js because original tools/js/serve.cjs has no .mjs MIME mapping. Do not change the shared server. Local test: node --input-type=module -e "import('./test_timeline.mjs')" (local package.json explicitly sets type=module).
