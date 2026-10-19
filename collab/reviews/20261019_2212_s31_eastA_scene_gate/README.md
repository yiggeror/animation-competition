# S31 east-A few-frame scene gate

Fixed source director/modules: 44883e8c502a6066a33c67be0e58cf7185554759. This package preserves all 30 exact local runtime files; 18 original modules remain byte-identical. The sole A scene module changes the approved east quilt edge and blocker; original B remains isolated.

From repository root:

```sh
cd collab/reviews/20261019_2212_s31_eastA_scene_gate
NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node scene_preview/render_keyframes.cjs
```

Runner uses installed Chromium (CHROMIUM_PATH override) and its own temporary local HTTP server. It captures clean original B180, A000, A116, then B180 after A; 4 PNGs plus exact registration, resource URL/status/error and A-to-B pixel reports. Require B channel difference 0, no pageerror/requestfailed or required asset failure. Preserve exact favicon response separately if present. Nothing here is a full S31 sequence or visual-ready declaration.

Review actual A images for east-gap grandma/half-open ground bundle and original crane visibility, foreground child's locked size, original lighting, real turtle two-rod grip, and crop/occlusion. Bag's physical base is ground [2.86,.30,.02], mouth [2.86,.30,.32]. The original 14px backdrop defocus is applied at 1920x1080 before the single 960x540 reduction.

Return actual outputs on a dedicated cloud branch; coordinator will place accepted media on this shared production branch for Opus. Do not modify production modules/EDL/audio or regenerate drawings during this render gate.
