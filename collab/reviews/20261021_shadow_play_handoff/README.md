# Shadow-play repair candidate handoff · 2026-10-21

This directory publishes already-produced candidates for Opus integration and review. It does not change production paths, previews, EDL, durations, S12, or S20. No new production was performed for this handoff. Do not treat publication as full scene acceptance.

## Integration

Copy only the seven files listed in manifest.json to their corresponding repository-root paths, removing the s26/, s29_s30/, or s32/ prefix. Review current production diffs first; do not overwrite newer collaborator edits. Shared renderer dependencies remain the repository versions. No runtime test stub, test harness, video, ZIP, or substitute font is included.

## S26

Three source files from S26_SHADOW_PLAY_CODE_REPAIR_V2_BOARDING_QA.zip: handdog.js, shots/s26.js, and shots/s26_motion.js. Removes artificial eye holes; continuous turns preserve hand/forearm volume; V2 corrects turtle boarding clearance without changing the later action.

Reported verification: 432-frame native Canvas sheet projection and independent review passed the eye-hole, turning, and boarding checks. This is not final WebGL lighting/camera/color acceptance. Render the complete 18 seconds, especially 6–9 seconds and 10.8–14.4 seconds, then S26 final 12 frames plus S27 first 24 frames. S27 calls the S26 endpoint and must be checked with the candidate.

## S29 / S30

Two source files plus the image-authored neck/shoulder extension from S29_S30_SHADOW_NECK_INCREMENT_20261021.zip. The helper composites the aligned extension behind the approved original head. Original head/hair/glasses/face and original color/normal/material maps remain protected; keep the existing original shadow at assets/chars/g29_prepare_blow_shadow.png. This is only the head-shadow neck/shoulder repair, not a replacement for other S29/S30 work.

Reported verification: protected-head pixel equality and continuous neck/body width checks passed; source composition and original sheet projection diagnostics were reviewed. Final complete GL rendering and S29 backstage occlusion remain unverified. Check preparation first/middle/last and the current 246-frame S30 frozen-head entry/middle/last, lower-frame exits, seams, lamp/sheet occlusion, and adjacent cuts. Preserve the intentional frozen pose.

## S32

Only js/code/s32.js from S32_SOURCE_DELTA.zip. Continuous window performance with distance-linked turtle steps and coordinated crane/turtle responses; original exterior, camera, 15-second timing and title fade remain.

Reported verification: complete 15-second 1920×1080 24fps Canvas preview, including the original Chinese title, passed independent review. The old no-title preview is superseded. Final production browser/export acceptance is separate. Load the existing assets/fonts/MaShanZheng-Regular.ttf (Git blob 11bbfb9867d70612158229d037e7a5f622bd0e38) with its existing OFL license; this is not a new font or a post-production title replacement.

## Provenance and originals

manifest.json records exact candidate byte sizes, SHA-256 and Git blob IDs, plus immutable baseline commit/path/blob references for original source, approved original shadow, and existing font. Originals already in this repository are referenced rather than uploaded again. Library review packages/videos are not needed to resolve production dependencies and are not copied into this public directory.
