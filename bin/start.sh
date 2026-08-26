#!/bin/bash
set -e

python -m alembic upgrade head

python bin/main.py &
API_PID=$!

python bin/outbox_worker.py &
WORKER_PID=$!

trap 'kill -TERM "$API_PID" "$WORKER_PID" 2>/dev/null' TERM INT

wait -n "$API_PID" "$WORKER_PID"
EXIT_CODE=$?

kill -TERM "$API_PID" "$WORKER_PID" 2>/dev/null
wait "$API_PID" "$WORKER_PID" 2>/dev/null

exit "$EXIT_CODE"