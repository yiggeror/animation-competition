# S20 coherent 127-frame candidate source handoff

Status: candidate, NOT final approved. Full GL lighting and original-speed 127-frame review remain pending. Native action-layer review is not a GL-render acceptance.

This folder contains the complete 165-file S20 production overlay, not merely the 55-file coherent-turn delta and not a standalone copy of the whole renderer. No MP4 or ZIP is included. The rejected old 129-frame candidate is not this sequence.

## Reproducible installation

1. Start with repository `yiggeror/animation-competition` at baseline commit `3f0b5172c3e6c66284dc57623bbc892ecc84439a`.
2. Copy this handoff's `repo/` contents onto that checkout's root, preserving paths. Do not serve this nested handoff directory as an independent root without the baseline engine.
3. Load `js/anim/s20_natural_20261021.js`. Render 1920×1080 at 24 fps, all 127 frames (0–126), duration 127/24 seconds. Use one fresh context and strictly await sequential frames; do not recreate a context for each frame to hide lifecycle errors.
4. Action is frames 0–78. Frames 79–126 use the eight-pose laugh source frames 144–191. Preserve `s20_laugh_compact8_drawn.js` SHA256 `937669cf80221170e22df4c05173b864b6db11d0f628d417f49488e2b586d7e3`, including its formal clear-entry lifecycle fix.

The overlay includes 6 JavaScript modules, 70 PNG files, and 89 JSON files. It preserves prior baseline production assets as well as the new coherent sequence. Superseded drawings retained in the overlay are not selected by the current sequence; `sequence.json` is the authoritative exposure/timeline table. The actual selected asset references are separately listed in MANIFEST.json.

## Verified scope

- All 55 coherent delta file hashes match the producer manifest.
- All 88 unique runtime sequence/laugh asset references exist locally; zero missing references.
- The 17-module public recursive import closure is readable at the fixed baseline commit, with Git blob hashes recorded in MANIFEST.json. Public engine modules are not duplicated or modified by this handoff.
- The complete overlay includes all eight laugh drawings with albedo/normal/material maps and camera/rod tables.
- Candidate uses same-registration whole-person drawings, fixed turtle physical size, held-plane projection, and existing GL lighting path. It must not be described as final passed until full GL and original-speed review are complete.

MANIFEST.json records every overlay file's size, SHA256 and Git blob SHA, exact runtime asset references, public engine dependency hashes and frame boundaries. This handoff adds a review directory only; it does not overwrite the branch's active production entry or other collaborators' work.
