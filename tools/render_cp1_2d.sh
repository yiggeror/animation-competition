#!/bin/bash
# 检查点 1（2D 版）的全部渲染：人物设定图 + 两段动作测试。用法：bash tools/render_cp1_2d.sh build/cp1_2d
set -e
OUT=${1:-build/cp1_2d}
mkdir -p "$OUT"
cd "$(dirname "$0")/.."
for a in turnaround expr hands; do node tools/js/snap.cjs js/sheets/characters.js "$OUT/chars_$a.png" 1920 1080 $a; done
node tools/js/frames.cjs js/shots/s06_test.js "$OUT/s06" --fps 24 --workers 3 --mp4 "$OUT/s06_crane_debut.mp4"
node tools/js/frames.cjs js/shots/s07_op_test.js "$OUT/s07" --fps 24 --workers 3 --mp4 "$OUT/s07_grandma_operates.mp4"
echo done
