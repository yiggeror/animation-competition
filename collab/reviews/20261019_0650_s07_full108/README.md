# S07 full108 production candidate: waiting actual render

Fixed first57 camera, phone, stool and contact choreography is preserved, including its original 16–38 and39–56 cuts. Eleven locked whole-figure tail drawings supply057/062/068/073/079/084/090/095/100/103/106 at the fixed native-to-scene registration. All31 PNGs are source Git blobs with no drawing/recolor/warp at integration. First57 authored actor descriptors and228 quarter-frame camera samples are equal after only URL remapping. The108 frame bindings cover0–107 without gaps.

The first57 standalone renders and each tail group already have bounded visual reviews. This integration has only syntax and structure tests so far. It is not ready until a real108f scene render checks the39→57 cut, walking support, pose-to-room scale,100 embedded-lamp switch and106 lift.

Lamp ownership: original scene tableLamp(0), including its original table shadow, is drawn only through099. Whole final100/103/106 PNGs own the one physical unlit lamp from100. Final106 lifts the same complete hand/arm/lamp group while leaving the103 table shadow in place; the final reviewer checked2329 visible shadow pixels unchanged, with40 newly uncovered pixels at y656. Do not redraw the old physical lamp/shadow over these frames. The usual character floor-contact projection remains.

Entry: js/anim/s07_drawn.js. Duration4.5s,108f24fps. Run:

node tools/js/frames.cjs js/anim/s07_drawn.js build/S07_full108 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S07_full108.mp4

Please deliver actual MP4, browser resource log, and decoded000/015/016/024/025/037/038/039/053/056/057/061/062/067/068/072/073/078/079/083/084/089/090/094/095/099/100/102/103/105/106/107. Prior candidate cache need not rerender. Ready/EDL/audio remain Opus/coordinator handoff after actual review.
