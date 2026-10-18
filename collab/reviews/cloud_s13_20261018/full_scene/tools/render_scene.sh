#!/usr/bin/env bash
set -euo pipefail
S13_REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)"
cd "$S13_REPO_DIR"
NODE_OPTIONS="--require $S13_REPO_DIR/collab/reviews/cloud_s13_20261018/full_scene/tools/use_system_chromium.cjs" \
  node tools/js/frames.cjs collab/reviews/cloud_s13_20261018/full_scene/s13_drawn.js \
  /tmp/s13_full_scene_frames --fps 24 --w 1280 --h 720 --workers 4 \
  --mp4 collab/reviews/cloud_s13_20261018/full_scene/S13_drawn_120f_720p24.mp4
