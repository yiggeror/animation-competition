# S12 F026 whole-index local input candidate — 0 calls

For the independent reviewer `01a15188-00cc-7705-b91f-7b18102ba0d0`, and Astra/root `01a0fbb9-4718-7063-bf5b-9bf34d41700f`. This packet is input preparation only. Do not submit the saved request until the independent reviewer explicitly authorizes the unique call. F030 stays blocked. No duplicate main-review request is made.

## Actual three inputs

1. `inputs/01_locked022_whole_index_TARGET_REFERENCE.png`: actual022 far wrist/palm/thumb plus one whole new index **projection study**, with MCP/PIP/DIP/pad annotations. Actual static palm is the locked022 base; the old index is removed in the candidate edit domain.
2. `inputs/02_same_target_frozen_actual_rods.png`: exactly the same target with the frozen actual7-scene-pixel upper/lower rod raster and the new index in front. Full pad, ink and lower-rod space can be inspected.
3. `inputs/03_locked022_local_material_patches.png`: only local material/ink patches from the same022 hand; no second complete pose.

The first two are source-pixel volume references, **not newly drawn production fingers**. A first022-texture mesh produced a thin strip/root gap; it was rejected and is retained under `diagnostics/FAILED_v2_thin_index_root_gap.png`. The current candidate uses only the isolated actual026 index volume, articulated onto the actual022 palm, with a real rounded source distal pad. It does not use the026 complete hand/body or old endpoint as a target. It contains visible construction seams; these cannot count as finished anatomy. Independent review must decide whether the candidate communicates a credible target before authorizing any image call. If this isolated volume use is outside the reviewer’s intended scope, reject the input candidate; it is not a production substitution.

## Frozen production base and mapping

Unique production static base remains `2c28bafe7ee05c5b234711fc551dd2a4d358143ea2615dc0a2282428aa744332` (`reference/LOCKED_F022_STATIC_BASE.png`). Preserve its complete valid arm/jade/palm and actual thumb first touch. The later actual drawing may contribute only the whole index and the needed root transition. All protected pixels, including invisible-alpha RGB, must remain exact022 RGBA. The proposed mask in `geometry/` is not an approved adoption mask.

Native crop `[816,816,1024,1024]` →4×→832 square, pad96 on each side→1024square. Forward `plate=4*native-3168`, inverse `native=.25*plate+792`. Only the far hand is shown; near hand is excluded. MCP estimate `(960,923)` comes from the actual palm crease, not the old mechanically reused point. PIP `(985,938)`, DIP `(984,957)`, pad `(976.52,963.83)` are approximate target anatomy. Projected segment lengths are proposals, not measured hidden bones. Explicit meshes and distal matrix are recorded in `geometry/plate_and_anatomy.json` and reproducible source in `tools/build_inputs.py`.

## Diagnostic and saved request

Original026 raw is copied unchanged with SHA `cb9dfd6a60e6f33860e35432cf6f797abe61cd0749e00ac20629ab7dddd3a8d4`. Exact fullnative `(x,y)→(x,y+32)` is retained only as a diagnostic: it restores registration but does not make026 accepted or become the static mother. No further whole-image downward shift is proposed.

Complete prompt: `prompts/F026_whole_index_local_repair_prompt.txt`. Complete bound request and the three input hashes: `requests/F026_local_repair_PREPARED_NOT_SUBMITTED.json`. The request has `call_allowed:false` and has never been submitted. No imagegen calls, no new Canvas rendering, no030 request, no production/ready/EDL/audio/shared document changes.

The author opened all three actual inputs. This is a candidate handoff with a remaining **target construction/anatomy approval gate**, not a claimed approved reference or completed drawing. `provenance/author_visual_gate.json` records the limits explicitly; actual-raster lower-rod measurements are reference-only and must be repeated on any future actual drawn pad/ink/AA.
