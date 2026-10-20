# Opening continuity production adoption and actual full-shot gate

Seven actual images at f5f7f8797aecc2a935761f2732fb7596668ab534 were independently and jointly viewed. The same-shot S07 scale, common pelvis region, mat support, full phone visibility, correct left short-end connector, slack cable, floor strip and wall lead pass this limited static gate. S01 versus S07 F008's existing 9.67% head-width reference difference remains disclosed; no claim that both fit a ±3% scalar tolerance.

The four production JS files are exact blobs of the approved 7749b635 candidate. Only their directory changes to js/anim; their same-directory helper import remains valid, and all other source/asset URLs are absolute production paths. No source PNG, exposure, EDL or audio edits. The complete three new scenes still require actual continuous inspection.

From repository root serve the fixed checkout on 127.0.0.1:8199. Run:
OPENING_OUTPUT_DIR=/tmp/opening-continuity-full node collab/reviews/20261019_1203_opening_full_gate/render_full_three.cjs

It verifies all four production sources, renders S01 84 / S04 72 / S07 108 distinct Canvas frames at 1920×1080 and 24 fps, streams three silent MP4s, retains specified key PNGs and every frame SHA, and compares the seven approved actual PNGs byte-for-byte. It does not copy or substitute old frames. Return completed clips as they become available, with CLIP_CHECK / FRAME_LEDGER / FULL_THREE_CHECK and exact HTTP errors. Decode each video independently for frame count and the retained keyframe sequence; visually inspect phone throw/cable at 000/003/006/008, S07 cut-in039/cut-out057, and inherited lamp/box ending100–107. Avoid re-running completed jobs if a later job fails. Audio reassembly stays with Opus after visual gate.
