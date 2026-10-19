Minimum production import: only js/anim/s06_drawn.js + assets/chars/s06/*.png (7 PNGs).
MANIFEST.json contains all eight exact paths and SHA-256 values. Parent owns production import; Opus owns S06 EDL module routing. No vendor, reviews, raw calls, or procedural helper copy is required at runtime.

Existing shared runtime references:
  js/paint/paintshot.js
  assets/paint/bg_01_room_wide.png
The previous approved native scene functions are unchanged. A production loader and renderFrame adapter were added; no exposure, phone/adapter endpoint, strip, lighting or pose geometry changed.

Current CPU evidence:
  ../s06_candidate/S06_F000-F085_FULL86_CANDIDATE.mp4
  1280 x 720 / 86 frames / 24 fps / 3.583333s / no audio.
  Rendered with @napi-rs/canvas from six arm states and one eye composite; pose holds repeat these seven rendered composites, including their grain samples. It is an actual timing/shape/contact preview, not a Chromium reference. Shared production renderPaint computes grain for every frame.
  Parent reviewed 4 contact before/after pairs, full tail composition and the single phone-glance eye state. Current S07 F008 comparison is range-only; actual S07 F000 remains the final cut-review dependency.

Formal browser boundary:
  This package has NOT been executed in Chromium here. Browser 1920x1080 alpha compositing, blur/filters, per-frame grain, final cut and full temporal read remain to be checked in the original cloud production task.
  The streaming script below uses one fresh independent browser page and the original repository serve/dev/view/paint pipeline, paints all 86 times, streams PNG directly to ffmpeg and retains only F000/F085 stills. No large PNG sequence is stored. The optional script is tooling only, not a runtime dependency.

From the production repository root, after import:
  node /absolute/path/to/render_s06_browser86_stream.cjs /tmp/s06_browser86/S06.mp4
  ffprobe -v error -show_entries stream=nb_frames,r_frame_rate,width,height,duration -of json /tmp/s06_browser86/S06.mp4
Expected: one video stream, 86 / 24/1 / 1920x1080 / 3.583333, no audio.

Existing repository renderer is also compatible:
  node tools/js/frames.cjs js/anim/s06_drawn.js /tmp/s06_frames --fps 24 --w 1920 --h 1080 --to 3.5833333333333335 --workers 1 --mp4 /tmp/S06_browser86.mp4 --clean 1
The existing renderer temporarily stores all PNGs; prefer streaming where disk is tight.

Sound candidates, S06-local frame/time: 11/.458333, 30/1.25, 46/1.916667, 70/2.916667. Original four sound events only; audio and EDL remain unchanged in this package.
Originals, actual requests, ordered inputs, registration/masks and failed F011 preserved in ../MINIMAL_HANDOFF_INDEX.json; no duplicated evidence bundle.
