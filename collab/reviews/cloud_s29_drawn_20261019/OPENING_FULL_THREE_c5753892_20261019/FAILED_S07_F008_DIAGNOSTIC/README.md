# S07 F008 approved-byte failure — finite diagnostic

Status: **HOLD**. The original continuous render stopped at F008; no S07 full108 delivery is accepted. S01 and S04 remain independently completed and published.

`ACTUAL_FAILED_S07_F008.png` and `APPROVED_S07_F008.png` are byte-exact copies. Actual SHA256: `77ef940e843e8db6b23152b0824d36f6aae110f8a415decc94fb75cd5b43ad40`; approved: `68ccf82317e5e7425fd136274615dc7d80a6596a6de723841f6a9a1cbbcb9685`.

662,702 pixels differ across the full 1920×1080 frame, maximum channel delta 3, alpha unchanged. The actual comparison sheet was opened: no visible subject/phone/strip/cable position shift was found at this finite scale; amplified differences show radial/vignette-like quantization rings and fine edge differences. This does not satisfy byte equivalence.

All 51 fetched JS/asset files match the approved seven-frame worktree byte-for-byte after mapping the four candidate module paths to their production paths. HTTP responses are all200, no request/page errors. Both executors use frame/24 and identical Chromium launch arguments. Grain resets a local seed from t. The sparse seven-frame execution and full sequential execution have different prior frame histories on their shared canvas. A context/raster-history explanation is a hypothesis, not an established root cause; no isolated rerender was performed here.

No renderer, HTTP server or publisher was started or restarted. Original production/executor files are unchanged. Only this diagnostic folder was added. The unrelated publisher.log final-exit append is intentionally outside this commit.
