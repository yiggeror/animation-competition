#!/bin/bash
# 第一个检查点的全部渲染：画风样张（全分辨率）、动态小样、设计稿。
# 用法：bash tools/render_checkpoint1.sh OUT_DIR
set -e
OUT=${1:-build/checkpoint1}
cd "$(dirname "$0")/.."
export PYTHONPATH=src
mkdir -p "$OUT"
python3 -m laidian.shots.style_samples "$OUT/samples" --w 1920 --h 1080 --ss 2 --moments 6,10,10w --cache "$OUT/cache"
python3 -m laidian.shots.design_sheets "$OUT/design"
python3 -m laidian.shots.motion_sample "$OUT/motion" --w 960 --h 540 --ss 2 --fps 24
echo done
