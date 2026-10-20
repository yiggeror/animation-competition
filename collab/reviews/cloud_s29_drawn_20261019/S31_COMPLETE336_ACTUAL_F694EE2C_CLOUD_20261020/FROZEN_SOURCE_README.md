# S31 complete 336-frame actual scene gate

Fixed candidate for the approved 14-second shot. The accepted native grandmother half-open bag remains unchanged; only the original crane and its two straight shafts move left 60 source pixels, retaining the two actual grip entrances. Camera, warm light, original B module, all 14 drawn child states, timing and EDL remain unchanged. Main review accepted the two actual warm-light A frames and the zero-call full-frame left-crane/contact proposal. Full-sequence visual and boundary review are still pending.

From this package directory run once:

S31_ALLOW_FULL_RENDER=1 S31_OUTPUT_DIR=/tmp/s31_complete_336_actual NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node scene_preview/render_complete_serial.cjs

Runtime source hashes are checked against S31_COMPLETE_RUNTIME_RELOCATION.json. The runner first captures an independent original-B-only self-repeat control, then opens a separate fresh page and renders 0–335 serially once. Frame 180 must equal the independent B self-repeat at exact RGBA zero difference. Output is one 336-frame 24fps 1920x1080 video-only MP4 plus six key PNGs and logs under /tmp; no full PNG sequence. Do not overwrite an existing output directory or restart a running render. Inspect actual results before whole-shot ready.
