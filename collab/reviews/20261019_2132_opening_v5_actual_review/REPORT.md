# Opening v5 actual delivery review

Fixed production source: `44883e8c502a6066a33c67be0e58cf7185554759`. Review: 2026-10-19 21:32 UTC.

## Result
The delivered v5 passes the checked picture boundaries and new audio signal/packaging gates. The movie itself is already on the shared production branch at `collab/reviews/20261019_opening_v5/opening_v5.mp4`; this review does not require an inaccessible cloud branch.

- MP4 SHA256 `9ca642f720bd2d75e7c6a5b80c0a9dc8c562324db92303f69edf286f56b0113d`; PCM SHA256 `084063581ce2e4e5a083865452e284460090e53d5ba701318fd3e833565f973e`, both match the delivery manifest.
- Actual independent decode: 974 frames, 1920×1080, 24 fps, 40.583333 seconds. All 78 selected actual boundary images were opened, including the five changed shots, the S06→S07 cut, and S07→S08.
- S01/S04 show the power strip and connected lines; S03a has no implausible foreground hand/watermelon; S06 stays prone beside the strip with actual remove/insert poses; the corrected S07 supine body, pelvis location, phone/lines and support remain consistent with the approved local repair. S08 actual ignition, match withdrawal, shade lowering and ending remain present. No new blocking picture defect was found in these checked images. This is decoded-image review, not a claim of subjective real-time movie playback.
- New audio was independently rebuilt from the six fixed original source files, without changing audio computation. The actual delivered 1,948,000 stereo PCM frames differ from the new normalized master prefix by at most 3 LSB, RMSE 0.013958 LSB (270 of 3,896,000 channel samples unequal).
- New S06 events at F011/F030/F046/F070 correspond to opening samples 1,294,000 / 1,332,000 / 1,364,000 / 1,412,000. Each −0.1/+0.3 second comparison window matches the rebuilt master within 0/2/2/3 LSB respectively. The obsolete blowing event is removed in this fixed source; the actual new PCM matches that new source.
- Actual AAC: best PCM alignment 0 samples, correlation 0.99941455, integrated −16.17 LUFS, true peak −4.41 dBTP. Container audio presentation ends 16 samples (0.333 ms) before the exact video end; this is sub-frame rounding, not a frame-level drift. Encoder padding is separately recorded in the packet evidence.

## Boundaries
No subjective listening is claimed. This review concerns the delivered new v5, not the old v4 audio. S06→S07 action ellipsis is the explicit director decision at the fixed source. The unmodified S06 EDL descriptive text still says “blow”; executable module and audio correctly follow the accepted no-blow action, so the descriptive text can be corrected during the next routine EDL edit. No timing change is required.
