# Finite S30 renderer diagnostic

Run once from repository root:

NODE_PATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules node collab/reviews/20261019_2226_s30_complete_scene_gate/diagnose_s30_finite_contexts.cjs

Two fresh contexts: [000,000] and [000,190,000,190]. Six PNG/JPEG with original RGBA hashes and three complete pixel comparisons; differences do not abort. Source 22 images/module/two helpers and preexisting assets checked before/after. No production edits, no288 rerender. Original full-video visual gate passed, original failed repeat000 pixels were not preserved and are not reconstructed here. This is only direct finite history isolation, not proof of arbitrary long-run bit determinism. Preserve exact differences, actual frames and context state.

Script SHA256 847cbff75617b0f091e7f97012cbc1ea54360dd2214639c090519bbaabbe4ff6.
