# Early small heel-release phase trial

Complete natural character with a small genuine hip/heel opening after LOW HOLD. Proposed trial is LOW → this pose → FIRST. Head/chest remain near the low endpoint and the remaining rise to FIRST is not yet resolved by static review. Choose short exposure from actual motion, not a long hold or a guaranteed mathematical midpoint.

PNG is 1920×1080 RGBA, with native canvas normalization and the one whole-person +1,+20 scene translation already baked. Runtime is identity; do not repeat the translation, resize by body bounds, or split head/limbs. Raw RGB is preserved; alpha removes generated background/props while retaining complete grey hair and shoe edges.

Consumer depends on the existing project js/paint/paintshot.js, js/anim/s12_drawn.js, js/lamp/crane.js, js/puppet.js and assets/chars/g12/sequence.json with its original background/contactShadow/boxFront. It retains original stage, lamp and camera. renderPhase selects apparatus 60 or 70 independently of exposure. Use top-level mapping states[key].rods, not historical free palm targets. Original crane joint A and finite rod length are preserved; G depth is a constructive 2.5D assumption, not a measured palm volume. This package does not replace the current shared light-path renderer; integrate its character and finite rods into that current renderer when testing.

Fixed review passed complete alpha and finite contact for trial. Fine pale antialiasing along both forearms remains a real dark-scene check item, not claimed fully clean. Offline complete alpha/finite contact checks do not establish browser-rendered continuity. No new generation beyond the recorded unique raw is included.
