# S07 first57 contact candidate, actual render pending

Adds only the three original S01 contact fields to `collab/reviews/20261018_1616_s07_first57_scene/s07_drawn_candidate.js`. All 20 PNGs, phone layer, timing and camera remain unchanged. Removing the three fields recovers the previous reviewed module byte-for-byte. Source tests are in TEST_RESULT.json.

The original 57-frame actual visual pass came from cloud commit 835803dd650ddf71224f6aec8cf00acee5a92849, with MP4 SHA256 d68f4833f21cf647b1e118548d6af63d4c0ee9c6a154a031132e71cdf455df11. Frames 25–38 show knee press, forward lean, hip rise, hand release and standing; 15→16 is the retained wide/close editorial cut, not continuous motion. Phone and repaired hair in 39–56 were actual-frame reviewed. That result does not cover the new contact shadows.

New exact render: node tools/js/frames.cjs /collab/reviews/20261018_1616_s07_first57_scene/s07_drawn_candidate.js build/s07_first57_contact --fps 24 --w 1280 --h 720 --workers 4 --from 0 --to 2.375 --mp4 build/S07_first57_contact.mp4

Inspect visible shoe/stool support at 0–15 and body/mat support at 39–56. Preserve the original 16–38 close camera; do not reframe to expose offscreen feet. 57–107 remain unavailable and throw. This is not whole-S07 ready and contains no audio decision.
