# S28 float depth correction candidate

Destination: `collab/reviews/20261019_0901_s28_float_depth/`. Reuses frozen76c44a19 stage and25 original locked PNGs. No picture regeneration, geometry shift, depth bias, shared shader change, audio or EDL change.

Root cause is confirmed against formal545341e:8bit card depth rounds at31.37mm steps, while original puppets are only5.23–6.99mm in front of the sheet along the camera rays. The shader strictly tests decoded card distance against sheet distance. Among5890 opaque green turtle pixels,5889 actual visible/hidden decisions match that rounding prediction(99.983%);2063 are falsely rejected. Float32 decoding falsely rejects0 of those samples, max error0.000119mm.

## Only precision/renderer-scope changes

The adapter still calls the frozen Float64 precompositor. It uploads the true ray-depth buffer asRGBA32F through the existing GL.texture Float32Array path, with exactW/H andNEAREST. R=depth/8; G/B come unchanged from the original material map; alpha stays its original value. Shader code is untouched.

All program and draw names are scoped to `s28_float_depth_20261019_v1__*`. Existing program cache slots are not overwritten. Scoped programs remain cached under their unique names. GL.prototype.texture/program/draw and the exact DEBUG property descriptors are restored in finally on success or failure. Frozen stage restoration ofS.occ/S.occBack remains. The mat texture is float for this draw; another ordinary render respecifies it toRGBA8 on its normal upload. This does not claim all host GPU state is reverted or that sharedS/GL can render concurrently. Render serially.

`stage_adapter.mjs` is the corrected stage entry. `entry_full192.mjs` delegates000–131 to it and132–191 to the already-approved phone-only code; the previous full192 entry is frozen and unchanged. Phone timing and composition are unchanged by this repair.

## Same three-frame formal gate, existing cloud only

From repository root:

```sh
python3 -m http.server 8196 --bind 127.0.0.1 > /tmp/s28-float-http.log 2>&1 &
S28_HTTP_PID=$!
mkdir -p /tmp/s28-float-three
S28_OUTPUT_DIR=/tmp/s28-float-three node collab/reviews/20261019_0901_s28_float_depth/render_three.cjs
S28_STATUS=$?
kill "$S28_HTTP_PID"
exit "$S28_STATUS"
```

Produces000/012/042 full scenes plus matching foreground/shadow andRENDER_SELF_CHECK. Each frame must report materialDepthUploadRGBA32F/NEAREST, floatMatUploads1, originalProgramSlotsUnchanged, GLMethodsRestored, DEBUGFieldsRestored, sceneProxyRestored. Review puppets unbroken, all four straight rods/hand entries,042 arm ordering and pure-human ground contact shadows. Do not substitute the old CPU pass for this gate.

## Checks already run

`node test_float_adapter.mjs`: Float32 depth andG/B pass; program/draw prefix pass; success and intentional-error GL/DEBUG restoration pass. Original formal-pixel correlation and Float32 numerical check are inFORMAL_STRIPE_CORRELATION.json. JS syntax passes. NewGPU formal rendering is NOT yet run locally. No local browser or privilege escalation was attempted.
