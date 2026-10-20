# S30 complete candidate: formal keyframe gate

The unused candidate module `js/paint/shots/s30_drawn.js` and all22 byte-identical locked native assets are installed. EDL, active shot routing, audio, paintshot and original s29_lamp are unchanged. This package is not a ready declaration.

From repository root, using the existing original cloud:

```sh
NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node collab/reviews/20261019_2226_s30_complete_scene_gate/render_repository_keyframes.cjs
```

Run only the default20 keyframes (0,26,27,39,40,54,96,114,120,132,138,143,144,146,147,162,180,189,190,287), plus five unsaved cross-renderer diagnostic repeats. Do not use --all yet. The runner verifies raw/module/helper/old-shadow-asset SHAs, preserves exact failure URLs, separately records favicon204, and fails renderer-repeat mismatches. Return actual_browser_frames including20 images and report.

Main review has seen the CPU keyframe/lamp/contact-shadow boards and source logic. Actual browser scene continuity, especially original frozen-head branch190–287 and the189→190 transition, is still pending. Preserve old files and report a real failure rather than rewriting the candidate to bypass its checks.
