# Opening continuity: actual seven-frame candidate gate

Status: review candidate only. Production modules, source PNGs, exposure, EDL and audio unchanged.
Base: 7442d9bf860347dd8810264ac32575cf4930b6d5; director instructions f4dca238dd82b258405601c709de129938fbe705.

## What changed
- S07 F039/F043/F046/F049/F053 use a single registration s=0.23312714776632304, x=327.8295532646048, y=506.45498281786945. Same drawing pixels, natural common pelvis vicinity, phone remains x430/y533/sc0.16. Body contact shadow follows the same whole layer.
- S01/S04/S07 gain one matching floor power strip and phone cable at the mat head edge, plus the power lead to the wall socket behind the TV cabinet. It receives the original scene lighting and emits no light.
- S07 phone cable endpoints follow the actual held/landed exposures; F008 onward remains connected to the fixed landed phone. S06 uses the same physical prop in its newly drawn close view, prepared separately.
- No changes to original lamp, matchbox, grandma walk, scene camera, or S03a foreground-removal correction.

## The reference-size conflict, not a 0.7 scaling assumption
Measured main head silhouette (without pigtails/tuft), normalized to the same room plate:
S07 F008: 424*0.16=67.84; old F039/F053: 291*0.2475=72.0225 (+6.17%). S01 F000: 465*0.16=74.40 (+9.67% vs F008).
One scalar cannot be within 3% of both the current S01 and S07 F008 references. This candidate follows the same-shot F008 head scale and real body/phone composition; it does not claim both references match. Please judge the actual seven images before any production adoption. No across-shot redesign is proposed.

## Actual browser gate
From repository root, serve this exact checkout with `python3 -m http.server 8199 --bind 127.0.0.1`.
Run `OPENING_OUTPUT_DIR=/tmp/opening-continuity-seven node collab/reviews/20261019_1140_opening_continuity_candidate/render_seven.cjs`.
It renders S01 F000, S04 F008 and S07 F008/F039/F043/F053/F057 at 1920x1080,24fps timestamps. Retain all seven original PNGs and SOURCE_AND_HTTP_CHECK.json; report missing resources/page errors exactly. This is a small composition gate, not a complete-scene visual pass.

Required visual checks: same-shot child scale and pelvis continuity; full prone/supine support; phone remains visible and connected; strip lies on the floor outside the mat edge; main lead reaches the same wall socket; original lighting and all other props remain unchanged. Do not restart completed full renders yet.
