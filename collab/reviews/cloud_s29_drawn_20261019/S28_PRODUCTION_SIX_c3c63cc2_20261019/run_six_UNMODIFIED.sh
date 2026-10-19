#!/usr/bin/env bash
set -u
cd /workspace/s28-production-six-20261019-c3c63cc2
REVIEW_DIR=collab/reviews/cloud_s29_drawn_20261019/S28_PRODUCTION_SIX_c3c63cc2_20261019
python3 -m http.server 8198 --bind 127.0.0.1 >"$REVIEW_DIR/http.log" 2>&1 &
S28_HTTP_PID=$!
trap 'kill "$S28_HTTP_PID" 2>/dev/null || true' EXIT
printf '{"http_pid":%s,"runner_pid":%s,"source_commit":"c3c63cc288807740114a4689af6ea18277a63794"}
' "$S28_HTTP_PID" "$$" >"$REVIEW_DIR/ACTUAL_START.json"
NODE_PATH=/opt/codex/cua_node/lib/node_modules NODE_OPTIONS="--require=$(pwd)/$REVIEW_DIR/capture_resources_ONLY.cjs" S28_OUTPUT_DIR=/tmp/s28-production-six node scripts/verify_s28_migration/verify_six.cjs >"$REVIEW_DIR/verify_six_actual.log" 2>&1 &
S28_VERIFY_PID=$!
printf '%s
' "$S28_VERIFY_PID" >"$REVIEW_DIR/verify_pid.txt"
wait "$S28_VERIFY_PID"
S28_STATUS=$?
printf '{"exit_code":%s}
' "$S28_STATUS" >"$REVIEW_DIR/ACTUAL_EXIT.json"
exit "$S28_STATUS"
