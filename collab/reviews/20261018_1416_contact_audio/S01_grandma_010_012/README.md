# S01 F010 / F012 thin handoff

F010 and F012 are final locked by coordinator and independent reviewer. Read provenance/F010_FINAL_PASS.json for gate details.

Only two new authored states here, derived from locked F000 669a5e5b…ab9720. Existing F000 thin handoff is separate. One builtin generation per state; no new calls for seam repair. Final pixels, raw outputs, exact model inputs, masks, registration and checks are preserved.

- F000 frame0 hold10: closed pod, ready.
- F010 frame10 hold2: still fully closed, fingertips compress and near palm lifts slightly.
- F012 frame12 through27: split shell lips and two beans nested; no falling bean. F020 Xiaoman state belongs to implementation, not this layer.
- F028 and later are not produced. F012 remains the S04 shared first state; this package does not implement S04.

1024×1536 RGBA, fixed world transform scale .2734375 plus (730,375). Each PNG already contains the single basin. Do not layer a duplicate basin. Keep neutral source colors; implementation applies scene light once. Composite actual authored states and hold them; no crossfade or independent rigid motion of fingers/pod.

F010 natural near wrist is approximately asset(548,905), 5asset/1.367scene above F000. F010 uses its own same-call natural single green jade at anatomical LEFT wrist. It is not F000 jade pixel-identical. F012 retains F000 wrist/jade pixels. All actual points are visible painted estimates ±2asset, not hidden skeleton measurements. geometry/F000_F010_F012_actual_registration.json supersedes old proposed wrist locks.

The real same-basin protection mask changes0 in F010. Outside explicit union/head and y990+ change0; necessary same-call wrist/forearm copied until x647–653 where source silhouette meets naturally. F012 union/head/jadebox/y950+ change0. These are technical bounds, not a substitute for visual acceptance.

Preview is 28 actual authored frames, 24fps, ending F027. Quarter-speed copy is diagnostic only. Scene lighting and real scene composite are integration review, not asserted by this neutral author preview.

Author made no repository writes. Coordinator owns final repository path/commit mapping.
