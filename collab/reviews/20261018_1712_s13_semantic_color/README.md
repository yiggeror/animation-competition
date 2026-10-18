# S13 original-pixel semantic color correction, actual full scene pending

Coordinator and independent reviewer inspected all16 original/corrected drawings plus per-state eyes/mouth/collar/cuff edges. F000 and F018 remain byte-for-byte originals; only the other14 production PNGs under assets/chars/x13 change. The scene module, exposure, geometry, alpha, deep linework and protected features remain unchanged. No new image-generation request was made.

The original-color accumulation is corrected by separate per-state hair/skin/dress masks. Existing skin gradients, eyelid gray shadow, eye whites, mouth details, white collar and dress dots remain. Four previously approved samples keep their exact SHA. FROZEN.json records all16 source/candidate SHA256 and effective-color checks; independent16_hash_alpha_line_outside.json independently verifies all16 hashes and zero alpha/line/outside-mask changes. Means are material-specific, not claims that all lighting/shading is identical. Original tail-hair shape remains a separate artistic observation.

The two contact boards and S13_isolated_before_after_120f_24fps.mp4 show unchanged16-state exposure on a neutral background. This is an actual encoded/decoded comparison for color continuity only, not a replacement for the real scene. Actual 120f/24fps/5s Canvas re-render is required before restoring complete visual ready. Current audio remains outside this color-only change.

Render: node tools/js/frames.cjs /js/anim/s13_drawn.js build/s13_color120 --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 5 --mp4 build/S13_color120.mp4

Decode all16 exposure starts 0,18,24,30,36,40,44,50,58,68,78,84,87,90,94,100 and119. Confirm skin/hair/dress continuity at original speed, preserved eye shadows and gradients, complete close at84, turn from87, final settling at100. Minimal reproduction archive includes exact masks/domains/scripts/source manifests, with source recovery instructions. All original generated files remain in repository history.
