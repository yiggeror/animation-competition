# S07 finite execution-history diagnostic — no full clip rerun

Frozen production source: `c57538925035118c0f8901fc2f22f478fbf803b4`. Four production hashes remain exact. The original full-three executor remains unchanged and stopped with exit 1 at S07 F008; S01/S04 completed deliveries remain unchanged.

A finite diagnostic rendered only S07: (1) fresh page direct F008; (2) another fresh page sequential F000–F008; (3) fresh page direct F008 with an explicit CPU-friendly `willReadFrequently:true` context as a diagnostic, not an adopted render setting. All three produced the approved F008 SHA256 `68ccf82317e5e7425fd136274615dc7d80a6596a6de723841f6a9a1cbbcb9685`. The sequential actual F008 was opened and inspected.

The original failed continuous-run F008 remains preserved in `../FAILED_S07_F008_DIAGNOSTIC/` with SHA256 `77ef940e843e8db6b23152b0824d36f6aae110f8a415decc94fb75cd5b43ad40`. The same frozen production code can reproduce the approved result in fresh execution. These tests narrow the issue to a difference in preceding execution/state; they do not establish a particular Canvas/GPU/JIT mechanism. The explicit readback-friendly context also passed, so a simple CPU-versus-GPU assertion is unsupported.

No S01/S04 frames were rerendered. No MP4/full S07 renderer was started, no failed bytes were replaced, and no expected hash was relaxed. This diagnostic is not S07 full108 acceptance. The original process is no longer running; a further S07-only execution decision belongs with main coordination under the unchanged strict sample gate.

Executable: `diagnose.cjs`; actual result logs: `RESULT.json`, `RESULT_FRESH_CPU_CONTEXT_F008.json`. The latter case was run via `DIAGNOSTIC_CASE=FRESH_CPU_CONTEXT_F008`. HTTP/page errors are empty and all responses successful in both runs. All diagnostic HTTP/browser processes exited.
