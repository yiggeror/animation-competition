# S28 full192 wrapper

Repository destination: `collab/reviews/20261019_0847_s28_full192/`.
Entry: `entry.mjs` exports `render(ctx,arg,W,H)`, `renderFrame(ctx,t,W,H)`, DURATION8, FPS24, FRAME_COUNT192. Numeric time and JSON `{t}` arguments work. Times outside0≤t<8 throw.

000–131 delegates unchanged to fixed76c44a19 stage module at sibling `20261019_0830_s28_stage_module/`, with existing25 locked PNGs at `20261019_0820_s28_locked_stage_assets/`. Stage initialization is lazy, so rendering phone frames does not initialize or change stage S. No old grandma closeup is reachable.

132–191 uses the original phone drawing from director-fixed30588f55, source blob322489b92daff614b2bde3042a04cc25e84dbce4. Two timing changes only:
- T_CUT3.2→5.5. The existing camera push0→12% now runs5.5→8s, with original start/end composition.
- scrOn(t≥5.5)=1. F132 immediately shows the original charging battery/lightning/1%; red-bar pulse still uses t−5.5.

PH, floor, bean shells, cable, phone, original light/glow/emit and icon are unchanged. `VALIDATION.json` verifies the complete PH→top code region byte equality after the one scrOn replacement. No audio or EDL changed. Full binding including authority quote is `FRAME_BINDINGS_FULL192.json`.

## Formal132/162/191 gate command (existing cloud, from repository root)

Uses8195 to avoid the queued stage review server on8194. Existing Playwright/Chromium only; no install or generation.

```sh
python3 -m http.server 8195 --bind 127.0.0.1 > /tmp/s28-full192-http.log 2>&1 &
S28_HTTP_PID=$!
S28_OUTPUT_DIR=/tmp/s28-phone-three node collab/reviews/20261019_0847_s28_full192/render_phone_three.cjs
S28_STATUS=$?
kill "$S28_HTTP_PID"
exit "$S28_STATUS"
```

EmitsF132_phone.png, F162_phone.png, F191_phone.png and PHONE_THREE_CHECK.json. OptionalCHROMIUM_PATH or S28_PREVIEW_URL override defaults. Browser-only phone gate is not claimed to have run locally.

## CPU checks

```sh
node collab/reviews/20261019_0847_s28_full192/test_wrapper.mjs
node collab/reviews/20261019_0847_s28_full192/test_phone_gate.cjs collab/reviews/20261019_0847_s28_full192/phone_insert.mjs
S28_HOST_ROOT="$PWD" S28_OUTPUT_DIR=/tmp/s28-phone-CPU node collab/reviews/20261019_0847_s28_full192/check_phone_cpu.cjs
```

The last command needs already-installed@napi-rs/canvas. It uses the exact existing renderPaint and phone drawing through CPU Canvas, without Chromium. This was run at1920×1080 for132/162/191: all icons opaque1; camera fit1/1.06/1.119901; green-lightning pixel counts2047/2291/2596. CPU phone rendering is an actual2D render, with browser/font raster parity still a separate gate. Stage full-scene lighting/depth validation remains with the queued000/012/042 package. No project aggregate test command exists in the read-only host snapshot(package.json has serve only).
