# S03 attention A4 delivery

All four frozen v1 candidates passed independent static review. 1672 × 941 RGBA, transparent. 24 fps; existing anchors unchanged.

## Final images and exposure

- `candidates/S03_F009_local_composite_v1.png` · F009–F012 (4 frames)
  SHA256 `00cf42fc11e50c8f8ae291fd64810a77a53b61ec4637b15ee98135a28d40c17a`
- `candidates/S03_F017_local_composite_v1.png` · F017–F020 (4 frames)
  SHA256 `a152d5062d37b2e2957a46cf29be15b225c558b0db557fb563e84e82edf5a1e8`
- `candidates/S03_F021_local_composite_v1.png` · F021–F025 (5 frames)
  SHA256 `2bfd3506bfab46a49c47d4cf4022de79e303e4f1f8c855aa5cb669d10be0c76e`
- `candidates/S03_F030_local_composite_v1.png` · F030–F033 (4 frames)
  SHA256 `6aad16ab0d7b60cc628be57ab58bde1f1cbb9799e8f6fcb3e26e6eab48afbd54`

## Evidence

- `manifest.json`: sources, actual dimensions, hashes, generation history and final status.
- `originals/` + `prompts/`: all 8 actual built-in imagegen calls, including rejected outputs, retained unchanged.
- `masks/`, `local_refs/`, `local_composition_manifest.json`, `F030_composition_manifest.json`: authorized local composition and positioning evidence.
- `final_pixel_checks.json`: zero changed pixels outside each explicit final mask; basin/plate bottom retained.
- `qa/attention_timeline_contact_sheet.jpg`, `qa/attention_head_contact_sheet.jpg`, `qa/A_neck_collar_boundaries.jpg`, `qa/F030_contact_triptych.jpg`; eight `qa/*_FINAL_*_onion50.jpg` boundary overlays.

## Scene handoff checks

- F021 → k03: check the old endpoint’s eye reopening and slight chin settling at actual exposure; do not redraw just for equal numerical steps.
- F030: minor hard corner near (630,653), inside lower left sleeve. v1 is frozen; clean locally only if it reads in scene.
- Legacy k01–k04 cool fill remains in locked base pixels. No added blue scene light; apply the shared scene-light treatment once.

**call_count: 8.** No further generation pending.
