# F037 independent original-pixel recomposition

Status: **diagnostic, blocked at far-sleeve contour, not adopted or locked**.

The complete new near arm uses the sole F037 call01 original translated uniformly by (0,+30) native pixels. Revealed garment uses that same original at (0,0). The F031 whole gripping hand and flashlight, already translated (0,-32) in the preposition, remain untouched. No generation, drawing, blending, resizing, limb splitting, rotation, or warp was used. Full RGBA pixels are copied exactly.

Run `python recompose.py` from this directory to reproduce the candidate, masks, source ID map, checks and whole/close-up previews. All writes stay in this independent directory. The original input mask, invocation freeze and parent scripts/files are unchanged.

## Deliverables

- `F037_independent_original_pixels_PENDING.png`: 1672×941 RGBA diagnostic candidate.
- `F037_full_gray.png`, `F037_full_dark.png`: whole-image QA.
- `F037_closeup_gray.png`, `F037_closeup_dark.png`: nearest-neighbor QA enlargement, not production artwork.
- `far_sleeve_source_conflict.png`: locked sleeve / native original-position sleeve / resulting contour comparison.
- `adoption_mask.png`, `arm_raw_dy30_mask.png`, `cloth_raw_dy0_mask.png`: binary adoption domains.
- `hard_protection_mask.png`, `far_visible_material_guard.png`: explicit frozen domains used.
- `pixel_source_ids.png`: 0 = locked preposition, 1 = original native coordinates, 2 = native translated down 30.
- `checks.json`: hashes, original RGBA provenance equality checks, guard checks, outside-input-mask difference disclosure, and source conflict sample pixels.

## Actual review

The old isolated skin fragment at (1019,591) is removed using native transparent pixels. The old U-shaped arm trace below the new elbow is replaced with complete original-coordinate returned garment and full white marks. The arm is continuous at both ends and there is no independently moved hand or forearm section.

One visible blocker remains: the original frozen far-sleeve tip is higher and farther right than the returned rounded far-sleeve contour. Combining their available pixels produces a two-pronged notch. At (1004,610), the original pixel is old-arm skin AA, native original-position alpha is 2, and native translated-arm alpha is 0. At (1005,611), the original is old-arm occlusion ink and the two native choices have alpha 2 and 0. These do not provide the opaque new yellow sleeve contour needed to smooth the join. The preserved visible sleeve material cannot be trimmed or recolored under the current freeze.

The prior review's statement that the same native return supplied enough continuous sleeve material was too broad. It supplies a complete rounded sleeve, but that shape conflicts with the preserved original sleeve tip. This candidate therefore does **not** solve the final contour and must not be treated as final F037 or used to proceed to F042. A further local connection edit would need to fill only the newly exposed sleeve transition while preserving actual visible sleeve material, locked new arm, wrist/hand and all other hard domains; it is not performed here.

## Proposed next connection mask

`prepare_connection_mask.py` saves `PROPOSED_far_sleeve_connection_WHITE_EDIT.png`, a full-canvas technical mask, plus the unscaled crop and crop mask at `[950,560,1040,700]`, a labeled-by-filename overlay and `PROPOSED_connection_mask_checks.json`. Only the newly exposed far-sleeve joining material is editable. Existing near-arm material and original visible far-sleeve material/marks/folds are excluded. This is a suggested technical boundary for parent review, with **zero image calls**, and does not grant or claim Astra approval.
