#!/usr/bin/env bash
# Run in the existing Opus render environment from repo root, at the delivered commit.
set -euo pipefail
out=build/astra_three_shot_20261018
mkdir -p "$out"
for s in 03 07 08; do
  node tools/js/frames.cjs "js/anim/s${s}.js" "$out/frames_s${s}" --fps 24 --w 1280 --h 720 --mp4 "$out/s${s}_clean.mp4"
done
node tools/js/snap.cjs js/anim/strip.js "$out/s03_elbow.png" 2560 540 'S03|1.4166667:1.8333333:0.041666667|420,300,640'
node tools/js/snap.cjs js/anim/strip.js "$out/s07_roll.png" 2560 810 'S07|0.4166667:1.0:0.041666667|330,420,640'
node tools/js/snap.cjs js/anim/strip.js "$out/s07_rise_turn.png" 2560 1620 'S07|0.75:2.1666667:0.041666667'
node tools/js/snap.cjs js/anim/strip.js "$out/s07_grip.png" 2560 540 'S07|4.125:4.4583333:0.041666667|800,280,400'
node tools/js/snap.cjs js/anim/strip.js "$out/s08_ignite.png" 2560 1080 'S08|1.2916667:2.0416667:0.041666667|760,400,400'
node tools/js/snap.cjs js/anim/strip.js "$out/s08_lever.png" 2560 810 'S08|3.125:3.625:0.041666667|760,340,400'
sha256sum "$out"/*.mp4 "$out"/*.png > "$out/SHA256SUMS.txt"
