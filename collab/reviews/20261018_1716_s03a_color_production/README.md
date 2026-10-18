# S03a minimal crown-color correction + production asset paths

Three adopted states017/021/023 change only crown hair red channel by at most−2 through explicit continuous semantic weights. Face color-v2, skin gradient, deep lines, white collar, alpha and geometry remain identical. Material crown delta after correction is(3.59331,2.48025,2.28146), within±4. All three were independently viewed at native detail and dark background, not passed solely by means. No generation/resampling.

All9 character PNG references now use assets/chars/x03a/S03a_Fxxx.png. Six original images are copied byte-for-byte from collab/reviews/20261018_1305_s03a_all9/candidates/; the other3 are corrected versions. The foreground grandmother hand/melon remains untouched at its existing production path. In js/anim/s03a_drawn.js only X's base asset path changes; normalized module content is otherwise exact. Nine-state exposure and all light/camera/foreground motion remain unchanged.

Actual re-render pending: node tools/js/frames.cjs /js/anim/s03a_drawn.js build/s03a_color36 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 1.5 --mp4 build/S03a_color36.mp4

Decode all9 exposure starts plus35. Check no new color step through14→17→21→23→25, foreground contact and framing unchanged, all URLs resolve. Original36f motion/audio validation remains historical; color-only production version is not yet whole-scene visual ready. S03a_MANIFEST.json records exact before/after hashes. Semantic_masks_and_replay.zip preserves actual edit masks, protection/checks and author's original replay script with its stated source layout.
