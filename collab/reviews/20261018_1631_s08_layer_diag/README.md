# S08 F000 original-pixel arm/front layering diagnostic

Coordinator visually accepted the explicit mask and layer-order input at16:31UTC. Actual Canvas light/contact review is still pending. This diagnostic renders onlyt0, one frame, with no fire.

## Runtime

Entry `s08_f000_layer_scene.js`. Keep these five files together:
- s08_f000_layer_scene.js
- contract.js
- layer_contract.js
- frames/F000_body_behind_original_pixels.png
- frames/F000_forearms_elbows_original_pixels.png

Original root dependencies stay unchanged: `/js/paint/paintshot.js`, `/js/code/s08.js`, and their existing imports; named background `bg_01_room_wide` resolves to `/assets/paint/bg_01_room_wide.png`. Server/runtime files use.js.

Suggested pure-collab folder: `collab/reviews/20261018_1631_s08_layer_diag/`.

```sh
node tools/js/snap.cjs /collab/reviews/20261018_1631_s08_layer_diag/s08_f000_layer_scene.js /tmp/S08_F000_layer_actual_1920x1080.png 1920 1080 0
```

## Exact split, unchanged scene

Only the layer order changes: lamp/stool, original body-back pixels, original table front, original complete arms/elbows/hands/props pixels. Both layers remain1920×1080,sc1,x0,y0. Source locked mother c803571d4a6446e783fcbeb7aef41d65c1862ff3bf78a9a53f34b4631170e3f3 is unmodified.

The binary semantic mask is `masks/forearms_elbows_FOREGROUND_binary.png`. Body and front alpha are mutually exclusive; combining both without the table exactly reconstructs all original RGBA. Selected/source pixel values are unchanged, with no redraw, motion, interpolation, alpha overlap or double-darkening. Whole forearms and elbows are selected, rather than only slices belowy981. Lower torso remains behind the original table.

The scene's complete background, lamp, stool, table-front functions and light/glow/emit/camera/render controls are byte-identical to the original one-frame candidate. Lamp is still(1415,965.6), original table front startsy981. Ambient(.10,.11,.17), no lights, exposure1,vignette.5,grain7, camera960/540fit1, no flame/glow/smoke. No shared scene file has changed.

## Review meaning

Two elbows can read as resting at/slightly over the near table lip. The near elbow is close to the table's left corner. This split does not imply elbows are deep on the tabletop, move their contact points, add contact shadow, or validate actual lighting.

`references/F000_layer_gate_4panel.jpg` shows source, selectedmask, body and arms. `F000_layer_order_topology_NOT_CANVAS.jpg` is explicitly a neutral topology demonstration, not an actual scene render. Compare the new cloud frame against the original3f4c2f18 actual frame, paying attention to elbow/front-lip contact, silhouette, tabletop continuity and lower torso occlusion.

`LAYER_GATE.json` records exact split evidence; `TEST_RESULT.json` records hashes, dimensions, strictt0, unchanged source functions and layer ordering. New image generation0; new local Canvas renders0.
