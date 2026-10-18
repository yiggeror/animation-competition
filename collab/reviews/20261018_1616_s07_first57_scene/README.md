# S07 complete first57-frame scene candidate

All locked drawings required for frames0–56 are installed. Actual original-camera sequence review is pending. This is not the complete108-frame S07: frames57–107 deliberately throw and remain with the independent cloud work.

## Publish and render

Entry: `s07_drawn_candidate.js`

Minimal new runtime files: that entry and the five PNGs in `frames/`. The relative new-image URLs allow moving this whole folder without rewriting imports. Existing repository `/js/…` modules, background and 15 previously published image URLs must stay available. See `RUNTIME_FILES.txt` for exact runtime URLs, `DEPENDENCIES.json` for source blobs and `ASSET_MANIFEST.json` for every old/new image hash and registration.

Suggested publication folder: `collab/reviews/20261018_1616_s07_first57_scene/`.

```sh
node tools/js/frames.cjs /collab/reviews/20261018_1616_s07_first57_scene/s07_drawn_candidate.js build/s07_first57 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 2.375 --mp4 build/S07_first57.mp4
```

Render exactly57frames, 24fps,0–56. Keep the module's originalDURATION4.5 (108frames); it is not a shortened edit. Runtime files use `.js`, so the unchanged server supplies the correct JavaScript MIME.

## Exact assets and world mapping

New G025 holds25–27, G02828–30, G03131–33, G03434–36 and G03737–38. Each exact approved1024×1536RGBA is already registered; draw once at world `[730,375] + .2734375 × asset`. Each contains its own basin. No raw-to-canvas transform or extra basin is applied.

G037 final SHA: `4ebf2dc030fc8afd1cc53fb0269b31b0e4b7c4c416019ec47c3a045341ac4f8a`.

All15 prior image URLs are untouched. Original phone remains `.16 + (430,533)` behind supine Xiaoman. Five repaired Xiaoman tail images remain `.2475 + (339.7325,512.485)`. Their pixels, opaque red-tie/root preservation and accepted tail repair are not modified here.

Camera, background, stool, table lamp, darkLight, fan, coil and the full source suffix from XIAOMAN through renderFrame are byte-identical to accepted stage28 at commit2f6ae68e. This includes the existing upward camera follow during16–38 and cut to Xiaoman at39.

## Verified, and still to review

`checks/unchanged_result.json`: old43 frame descriptors exactly equal; old15 URLs and source-image SHA256 values equal; camera216samples equal; new5 images byte-identical to approved production sources;0–56 selectable;57–107 rejected. Original source snapshots are preserved in `provenance/`. The earlier partial candidate is retained separately at `../S07_F025_F034_insert_20261018_1616/`.

No browser/Canvas frames were rendered locally. Source equality is not a claim of newly rendered pixel equality or motion approval. Actual playback must especially inspect015→016 and the newly inserted25–38, then37→39. Check existing phone and repaired hair-tail readability in39–56. Static per-image acceptance does not establish temporal continuity. World soles around775 can be outside the approved close camera; do not describe them as visible.

Local structural/integrity test, from this folder:

```sh
node --input-type=module --check < s07_drawn_candidate.js
node --input-type=module -e "import('./test_unchanged.mjs')"
```

The test reads immutable local stage sources for hash comparison. It is not a browser dependency. No image generation, shared-repository writes, public-helper edits, audio/EDL edits or57–107 substitutions occurred.
