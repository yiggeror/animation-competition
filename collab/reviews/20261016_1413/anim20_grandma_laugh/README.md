# anim_20_grandma_laugh_bent — single-call generation handoff

## Deliverable

- File: `anim_20_grandma_laugh_bent.png`
- Actual dimensions: 1024 × 1536, opaque RGB PNG, 1,613,031 bytes.
- SHA-256: `cb814fe129b313b9a3f13b6ef6ce773ea2651bc28149d2cab0deeedcef1d7a4d`.
- One built-in `image_gen__imagegen` call. No retries, fallback, resize, crop, repaint, code image modification, or repository write.
- The output is a byte-for-byte copy of the original generated PNG. Its original source remains untouched at `/workspace/scratch/f060b5601755/generated_images/exec-0414a9e2-6f40-41eb-a4bc-f00585204fa3.png`.

## Inputs and request

The edit target is the approved single-person `anim_20_grandma_puppeteer.png` (1024 × 1536). The second input is the repository `grandma_expressions_current02.png`, used only for grandmother identity and the middle laughing expression. Both images were visually inspected before the call; the inspected expression copy was verified byte-identical to the repository version.

The actual full prompt is in `prompt.txt`; the exact request object is in `request.json`. The request asks for the same right-facing grandmother, fixed canvas and shoe positions, bending forward naturally with laughter, the nearer right hand at her abdomen and the far anatomical left hand retaining its jade bangle and a single short bamboo stick. All inherited clothing, hair, glasses and red-bead hairpin remain design invariants.

## Producer self-check, not independent approval

- A single full-body grandmother faces right. Both feet, the entire head/bun, both hands and the short stick are in frame.
- The laugh reads from closed smiling eyes and an open smiling mouth. The torso inclines forward naturally; the near hand gathers against her abdomen. The pose is a moderate forward laughing bend, not an extreme doubled-over bend.
- Two arms and two hands are visible. The far arm retains the green jade bangle and visibly grips one short stick. No additional stick, crane, lantern, long rod, furniture or floor line appears.
- Hair, red beads, round glasses, blue floral button shirt, navy trousers and black/white-soled shoes retain the master design.
- The canvas matches the master exactly. Read-only threshold analysis of fixed shoe regions found the near shoe's bottom at y1449 in both and far shoe's bottom at y1410 in both; the measured outer x bounds differ by no more than 1 pixel within these regions. These are approximate contour checks, not proof of pixel-identical registration. See `registration_check.json`.
- The background reads as pale grey with slight low-contrast texture/variation, rather than perfectly constant RGB. Sampled background RGB channels are approximately 210–215. The illustration has very soft form shading and no strong baked scene light or cast floor shadow.
- The full pose is ready for independent identity, anatomy, laugh-strength and swap-registration review. Production acceptance is not claimed here.

## Records

- `prompt.txt`: actual tool prompt.
- `request.json`: actual request arguments.
- `tool_result_metadata.json`: returned field names, verbatim output hint, original output path and data-URL validation information.
- `tool_response_complete.json`: complete returned image data and output hint. The image URL was expanded from the unchanged tool-generated PNG and matched against the actual result's length, prefix and suffix.
- `file_metadata.json`: output/input dimensions, modes, byte sizes and SHA-256 hashes, plus raw-copy verification.
- `registration_check.json`: read-only shoe-region comparison and background samples.
