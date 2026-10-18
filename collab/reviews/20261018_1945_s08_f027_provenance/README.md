# S08 F027 reproducible source supplement

Locked final SHA-256: `2dc0ee2bc06b4b872e0f79cbf4c1bd19b2ccaa160cba9b5feefd45f2a8e268ac`.
Repository destination: `collab/reviews/20261018_1945_s08_f027_provenance`.

## Result

The portable isolated replay exited 0. It reproduced the locked PNG byte-for-byte and every decoded RGBA pixel (0 changed pixels, maximum channel error 0). The isolated input directory contained only six PNG inputs, `replay_f027.py`, and `REPLAY_DEPENDENCIES.json`. The locked final was not present during replay; an external comparison read it only after the replay process exited. Actual command, timestamps, input list, environment and results are in `ISOLATED_REPLAY_LOG.json`, `ISOLATED_REPLAY.stdout.txt`, and `REPLAY_RESULT.json`.

This is deterministic postprocessing from the preserved global-call14 raw, not a reproduction of the image-generation service. No new generation or network call was made. Original SEALED files, the locked final, and original scripts were not modified. The script enforces declared file reads and writes to a new output directory using a Python audit hook; this is not an operating-system security sandbox. Standard runtime-library reads remain allowed.

## Reproduce

Use Python with the recorded versions: Pillow 12.3.0, NumPy 2.3.5, SciPy 1.17.0, zlib 1.3.2. These packages were already installed; this supplement installs nothing.

From this package directory:

    python run_isolated_replay.py --sandbox /tmp/f027-replay-new

For an additional decoded-pixel comparison after replay, supply the separately preserved final:

    python run_isolated_replay.py --sandbox /tmp/f027-replay-new --verify-against F027_FINAL_LOCKED/S08_F027_grandma_match_box_RGBA.png

Choose a fresh directory each time. Existing output directories are rejected. The minimal replay itself is:

    python replay_f027.py --out /tmp/f027-output-new

## Six computational inputs

1. Preserved global-call14 raw.
2. Locked F025 full RGBA.
3. F025 true near-hand/match footprint.
4. F025 whole closed far-hand/jade/transparent-seat footprint.
5. Actual submitted 3× white edit mask, including the final proximal collar release.
6. Frozen true jade material-and-outline guard.

`REPLAY_DEPENDENCIES.json` provides all relative paths, SHA-256 values, Git blob SHA-1 values, sizes, existing repository source paths and expected final checksums. F025 source image and both footprints reuse already-present repository blobs. The existing call14 raw is also reused.

## Why the original 35-item index was insufficient

All 35 original entries were present and matched their stated checksums. However, four computational dependencies were absent from that index: the F025 source image, its two original footprints, and the true jade guard. Original scripts also referred to absolute production paths, generated intermediates and diagnostic-only files. They are retained unchanged as documentary source; do not run them against production directories.

The portable script reconstructs exact preplacement, scene white mask, near/far hard guards, registered raw, all semantic masks, v6 output and final material correction. It does not need old intermediate PNGs. Derived preplacement and guards were checked against the production input with zero differing pixels. The white mask has zero intersection with the blue-cloth and box guards, making those redundant in the color eligibility calculation. The final far hard guard retains 18,756 pixels and correctly releases 183 proximal collar pixels.

The old `build_input.py` alone predates the collar refinement. This replay uses the actual submitted final mask instead, preserving the reviewer-approved release. Original operation order, data types, alpha behavior and rounding are maintained, including the original uint8 expression in the 22-pixel near-collar transition.

## Provenance and delivery

`SOURCE_MANIFEST_ORIGINAL_35.json` preserves the original index; its files are retained at the same paths relative to this package. Actual five generation inputs, successful request/prompt, six-input validation failure and exact error, original registration/repair/color scripts, masks and final contract remain preserved. The first submission returned no raw because the tool accepted at most five reference paths. The corrected second submission produced the adopted call14 raw. Replaying this supplement adds no image-generation calls.

The other four generation references and diagnostic material measurements document the generation and review, but are not computational dependencies after raw preservation. No redundant preview boards or replay-output PNGs are added to delivery.

The final lower-turn shading remains an approved new-view shading diagnosis, not a claim that every skin pixel lies within ±4 of the original color reference.

`ROWS.json` is the coordinator transfer list, with uniform keys `local`, `path`, `sha`, `bytes`, `upload`. Here `sha` is the Git blob SHA-1; `upload:false` reuses an existing repository blob. The rows target only the provenance directory above. `ROWS.json` itself is transfer metadata, not a recursively hashed package member.
