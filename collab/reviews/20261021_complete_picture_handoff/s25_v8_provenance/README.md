# S25 V8 local candidate
V3, V6 and V7 were rejected by user. V8 independent continuous-frame review found the downward reversal removed, with no renewed arm/torch penetration or identity jump; user dynamic review pending.

V6 defect: right hand changes from small/thin R036 to fat/stubby R041 then slender R044/R048. The first two source families are now inactive, not merely rescaled. V8 uses the same slender R044 art at fixed scale throughout release/side-exit/rise. Wrist position and visible lower-arm entry root jointly specify a continuous whole-limb rotation path. The still-gripping transition starts elbow recovery before release. Fixed torch and support are not moved to conceal intersections. The shoulder is outside the picture and has not been visually checked.

F068 registration .9→1.0 and F078 .9→1.14 use fixed destination wrist placement to remove undersized intermediate hand identity; no general frame resize. All changes require full-chain comparison, not only individual hand checks.

Used source paintings: 11 retained originals (000/006/012/018/024/029/064/072/084/106/110) and 9 generated source PNGs (2 grip; release44 right; release48 left;52/56/60/68/78). Total20 source paintings. L/R splits, reuse, and exposure count do not represent additional drawings. This iteration has no newly accepted generated painting: a three-pose strip was rejected and excluded. Previously generated valid art is reused and registered consistently.

108 output exposures at24fps=4.5sec. EDL delta−36 exposures/−1.5sec relative to original6sec S25; full film NOT changed. Two final mouth openings retained. No repository sync or external upload performed.

Active per-exposure layer mapping: EXPOSURE_MAPPING.json. Archived/inactive candidate assets remain for reproducibility but are not active drawings; specifically R036/R038/R041/R048 and F038/F041 are not consumed into rendered pixels. Registration scripts retain historical branches and should not be rerun indiscriminately. Ready-to-use registered candidate PNGs and render code are authoritative.

Render: node render_candidate.cjs. Encode: ffmpeg -framerate 24 -i candidate_frames/%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p output.mp4 (use spaces before numeric flag values).

V8 change: remove the invented downward detour. Wrist y at exposures24/27/31/37/41/42.5 is955/945/930/900/880/875, never reverses down. Horizontal clearance occurs immediately beside the lamp, then the same slender hand rises into the gesture. Source pictures, scale, exposure schedule and final dog action unchanged. V7 rejected because down-then-up was purposeless even though its collisions passed.
