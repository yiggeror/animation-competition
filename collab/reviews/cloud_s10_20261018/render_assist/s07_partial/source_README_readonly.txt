# Actual-scene render candidate, partial S07 only

This small package prioritizes real rendering. Raw inputs/prompts/masks for both newly locked states are preserved locally and will follow in their author provenance packages; they are not claimed present in this minimal package.

- S07 F022 f35bf87d46c1096fa336a2565699eae9f6be93f9b58ba392c0701f0f126c82db: true empty hands released from bowl, coherent natural whole arms/single jade, same raw joins and neck cleanup independently reviewed. `.2734375+(730,375)`; basin embedded once.
- S01 Xiaoman F000 de7b4b8c2c3918a4b6f05c451fb675e56a9677d3cb94c18ae106e13c848d061c: 1792x1024 RGBA; `.16+(399.28,533)`. Whole neck/knees/contact static gate passed. Head height70, natural width73.437, center(614.115,589.260); old original head target was superseded explicitly. Alpha-zero pixels can retain irrelevant old RGB; inspect alpha-composited image, not RGB alone. Do not substitute this playing pose for S07 release pose.

## S07 candidate

` s07_drawn_partial_candidate.js ` uses exact 1672x941 frozen scene and original camera/light/props, image-only people. No public or main implementation modules changed. It intentionally throws on missing visible states. It is NOT a complete shot and NOT ready for final acceptance.

Render only the two completed ranges at1280x720/24fps, existing cloud Chromium environment:

```sh
node tools/js/frames.cjs collab/reviews/20261018_1425_s07_partial_scene/s07_drawn_partial_candidate.js build/s07_first25 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 1.0416666666666667 --mp4 build/S07_first25.mp4
node tools/js/frames.cjs collab/reviews/20261018_1425_s07_partial_scene/s07_drawn_partial_candidate.js build/s07_x39_56 --fps 24 --w 1280 --h 720 --workers 4 --from 1.625 --to 2.375 --mp4 build/S07_x39_56.mp4
```

Expected25 and18frames. Retain logs, actual MP4 and decoded0/2/3/5/6/7/8/15/16/17/18/21/22/24 for first segment;39/42/43/45/46/48/49/52/53/56 for second. These are absolute scene frame indices, second MP4 local indices subtract39. Check actual stool/hip and floor contact, single basin, two-hand release, phone landing and independent phone behind supine person, and camera cuts. Node structural checks are not visual acceptance. No audio here.

Unfinished25–38 and57–107 deliberately reject rendering; offscreen flip/turn not invented as new successful animation. Final108-frame shot awaits drawn grandma rise/walk/handle states and actual whole-shot review.
