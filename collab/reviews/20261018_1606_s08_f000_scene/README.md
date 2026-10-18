# S08 F000 single-scene diagnostic

One real scene frame requested. Fixed t=0,1920×1080, DURATION1/24 and FRAME_COUNT1 for the diagnostic only. Full S08 remains6seconds elsewhere; this is not32 completed states. Every nonzero time throws.

Mother PNG is exact finally accepted c803571d4a6446e783fcbeb7aef41d65c1862ff3bf78a9a53f34b4631170e3f3. It is already registered1920×1080 and placedx0,y0,sc1. Original match and box are included in this drawing. No code character, extra match or extra box.

Only lamp's worldx changes1380→1415 (+35). Bottomy965.6, scale14/18.5, mirror-x, low glass and actual code lamp remain. Wick top is(1415,794.572973). No match/wick fire, glow or smoke at0.

Original room crop(980,160,640,360), blur22, destination(-80,-60,2080,1200); original table surface950.2–981 startingx764; original tableFront function/layer retained exactly. Original stool is retained but its topy1163 is below the1080crop. Camera(960,540),fit1; ambient(.10,.11,.17),lights[],exposure1,vignette.5,grain7.

OPEN DIRECTOR QUESTION: new real elbow tips extend approximatelyy990–998. Original foreground table startsy981 and may hide their lower edges. This package deliberately keeps the table/camera unchanged for actual scene diagnosis. No draft table polygon is substituted, and no framing correction is pre-approved by this code. Inspect both elbow tips, blouse cutoff, lamp/glass versus far hand, whole-frame scale and dark readability in the real output.

## Publish and render

Copy this entire folder intact to repository path:
collab/reviews/20261018_1606_s08_f000_scene/

Runtime entry is s08_f000_scene.js. Relative runtime dependencies are contract.js and frames/S08_F000_grandma_match_box_RGBA.png. Absolute repository imports are /js/paint/paintshot.js and /js/code/s08.js; original background is assets/paint/bg_01_room_wide.png. Full source/dependency hashes are inMANIFEST.json. All runtime files use.js, matching the unchanged original server MIME types.

From repository root, exact single-image command:

    node tools/js/snap.cjs /collab/reviews/20261018_1606_s08_f000_scene/s08_f000_scene.js /tmp/s08_f000_scene.png 1920 1080 0

Equivalent explicitly one-frame batch command:

    node tools/js/frames.cjs /collab/reviews/20261018_1606_s08_f000_scene/s08_f000_scene.js /tmp/s08_f000_scene_frames --fps 24 --w 1920 --h 1080 --from 0 --to 0.041666666666666664 --workers 1

Expected batch file00000.png only. Do not use--mp4 to imply a full shot, and do not render missing later poses.

Local integrity test (not visual rendering):

    node --input-type=module -e "import('./test_contract.mjs')"

Nestedpackage.json explicitly specifies module mode. TEST_RESULT.json records zero actual Canvas renders here. No local browser render is asserted. Parent coordination publishes and sends this to cloud Canvas.
