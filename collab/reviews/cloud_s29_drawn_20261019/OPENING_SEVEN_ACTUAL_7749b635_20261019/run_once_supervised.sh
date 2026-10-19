#!/usr/bin/env bash
set -u
cd /workspace/opening-seven-20261019-7749b635
REVIEW_DIR=collab/reviews/cloud_s29_drawn_20261019/OPENING_SEVEN_ACTUAL_7749b635_20261019
python3 -m http.server 8199 --bind 127.0.0.1 >"$REVIEW_DIR/http.log" 2>&1 &
OPENING_HTTP_PID=$!
trap 'kill "$OPENING_HTTP_PID" 2>/dev/null || true' EXIT
OPENING_OUTPUT_DIR=/tmp/opening-continuity-seven node collab/reviews/20261019_1140_opening_continuity_candidate/render_seven.cjs >"$REVIEW_DIR/render_actual.log" 2>&1 &
OPENING_NODE_PID=$!
printf '{"supervisor_pid":%s,"http_pid":%s,"node_pid":%s,"source_commit":"7749b6355e46448c13de71b635dfb0700c0addde","status":"RUNNING"}
' "$$" "$OPENING_HTTP_PID" "$OPENING_NODE_PID" >"$REVIEW_DIR/RUN_STATE.json"
wait "$OPENING_NODE_PID"
OPENING_STATUS=$?
printf '{"supervisor_pid":%s,"http_pid":%s,"node_pid":%s,"source_commit":"7749b6355e46448c13de71b635dfb0700c0addde","status":"FINISHED","exit_code":%s}
' "$$" "$OPENING_HTTP_PID" "$OPENING_NODE_PID" "$OPENING_STATUS" >"$REVIEW_DIR/RUN_STATE.json"
exit "$OPENING_STATUS"
