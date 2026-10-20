# Opening v4 actual audit — fixed 571cf92d

Actual opening_v4.mp4 and opening_pcm.wav both match the delivered SHA256SUMS. Video: 974 frames, 1920×1080, 24fps, 40.583333 seconds, covering S01 through S08 inclusive. S09 and S15 are not in this file.

The six fixed audio/source files were exported unchanged and the original build.py was executed independently. Delivered PCM vs the first 1,948,000 samples of that rebuilt normalized master: max 3 LSB, RMSE 0.0137445 LSB, only 265 of 3,896,000 channel samples differ. Rebuilt master SHA256: 9e902d495adb0289d6963deefdf8b5959829ce9f20a1b7459aba6c189980f249. This verifies the new sound program is in the actual supplied PCM, without claiming possession of the original Opus machine master.

Actual AAC vs supplied PCM: best lag 0 samples, correlation 0.999468722, true peak −4.25 dBTP, integrated −16.14 LUFS. AAC presentation ends 16 samples (0.333ms) before exact video/PCM length because of millisecond edit duration; this is a tiny container tail rounding, not a visible-frame sync error.

Actual video: 50 independently decoded scene edges and S07/S08 action boundaries were viewed. All 108 S07 and 144 S08 decoded low-resolution frames were also compared to the accepted full-scene references; small encoding differences only. Actual cut S07 F107→S08 F000, single lamp/retained box, lamp ignition and settled ending are present. This is decoded-picture review and signal verification, not a claim of subjective full-speed playback or listening.

## One small sound-timing item for Opus
The new source comment says the offscreen turn/roll cloth sound stops before S07 F039 (1.625s). But bamboo_mat(0.7) begins at F036/24 +0.02 =1.52s; deterministic dry transients continue to2.162979s (aboutF052), nominal clip ends2.22s. 77.8% of this isolated element's dry energy is afterF039. The delivered PCM matches this new source, so this is present in the actual audio. Suggest shortening this particular new dry bamboo clip to0.10s at the current start (ending1.62s), with natural reverb tail, or moving the complete clip earlier if preferred. Do not regenerate pictures or rerender video for this audio-only adjustment. All other actual S07 specified cue offsets and S08 action points are represented in the fixed source.

Sources, actual probe/metrics, source manifest, original exact build log, and representative decoded edges accompany this note.
