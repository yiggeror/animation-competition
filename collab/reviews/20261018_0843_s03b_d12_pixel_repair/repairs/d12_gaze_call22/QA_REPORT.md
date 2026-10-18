# S03b d12 call22 eye-only in-between

## Result
Single built-in image_gen call completed. Project total: 14 initial + 8 repairs = 22 calls. No retry or extra generation. Local candidate only; no repository, shared implementation, deployment or upload changed.

Edited only two small eye/upper-lid polygons, using the generated pixels at the original head scale. Pixels outside those polygons come exactly from the coordinator's seam-v3 candidate, verified SHA e860f258d35358785aab76f0a4a7770a8a42335b6a82bf810b5da6b1d3ec1147.

The gaze clearly begins moving screen-right/down and upper lids are softer. Both pupils remain spatially between actual d11 and d13; this result advances toward the latter half of the interval, especially the screen-right eye, rather than being a strict 50% interpolation. Visual estimates of pupil centers in full-frame coordinates: d11 (710,285)/(803,315), d12 about (728,296)/(832,326), d13 (736,301)/(840,331). These are manual visual estimates, not calibrated measurements.

The head silhouette, hair, ear, eyeglasses rims/bridge, nose, mouth, jaw, neck and body were not replaced. Literal 3-degree head rotation is therefore NOT claimed. This is the gated eye-expression repair only.

## Pixel invariants
- Full canvas: 1670 x 942 RGBA.
- 4,060 changed pixels, all inside the two eye polygons.
- Outside-mask changed pixels: 0.
- All pixels below y=341: byte-identical to seam-v3.
- Thus arm, hand, watermelon, torso and basin remain byte-identical to seam-v3.
- Candidate SHA256: 66e6caaf685b8d7cca105523be3ade49fc4ea7253ffda10346aac37afb0188cb.

## Artifacts
- Candidate: composites/S03b_d12_f28_call22_eyes_on_seams_v3.png
- Full-canvas eye patch: composites/S03b_d12_call22_eyes_patch_rgba.png
- Full-canvas mask: composites/S03b_d12_call22_eyes_mask.png
- 512x512 head-crop eye patch: composites/S03b_d12_call22_eyes_patch_head512_rgba.png, paste origin (608,0)
- Head comparison: composites/head_triptych_final.png
- Eye comparison: composites/eye_triptych_final.png
- Pixel checks: composites/pixel_lock_checks.json
- Raw generated image: outputs/call22_generated_raw.png
- Generation prompt: prompt_prepared.txt

## Visual check
Viewed full original d11, d13, coordinator body, native 512 head references, generated image, raw eye comparison, composited eye comparison, composited head comparison and full final frame. No obvious double pupil, broken frame or patch edge is visible at normal presentation size. The isolated eye motion reads independently of the preserved head silhouette. Final temporal suitability remains for coordinator review in the actual 11-12-13 timing.
