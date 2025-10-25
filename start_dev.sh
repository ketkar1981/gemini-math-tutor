#!/usr/bin/env bash
# Start script for Gemini Math Tutor (backend + frontend) with basic checks
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGDIR="$ROOT_DIR/.devlogs"
mkdir -p "$LOGDIR"

echo "[start_dev] root: $ROOT_DIR"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

# 1) Check GEMINI_API_KEY is set
if [ -z "${GEMINI_API_KEY:-}" ]; then
  fail "GEMINI_API_KEY is not set. Set it in the environment or add it to your Codespaces secrets."
fi
echo "[start_dev] GEMINI_API_KEY is present (not displayed)."

# Immediately verify the GEMINI API key by running the bundled key test script.
# This runs before starting the backend so we fail fast if the key is invalid.
resp_file="$LOGDIR/gemini_key_test.out"

# Run the test script, print up to 200 lines of its output, and fail on non-zero exit
python3 -u "$ROOT_DIR/backend/gemini_key_test.py" --prompt "Say hello in one sentence." >"$resp_file" 2>&1
test_exit=$?

sed -n '1,200p' "$resp_file" || true

if [ "$test_exit" -ne 0 ]; then
  echo "[start_dev] gemini_key_test failed (exit code $test_exit). See $resp_file for details." >&2
  fail "GEMINI API key test failed (exit code $test_exit)"
else
  echo "[start_dev] gemini_key_test succeeded."
fi

# Helper to kill background processes on exit
children=""
cleanup() {
  echo "[start_dev] cleaning up..."
  if [ -n "$children" ]; then
    kill $children >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

# 2) Start backend (uvicorn) in reload mode
echo "[start_dev] starting backend (uvicorn) ..."
uvicorn backend.gemini_server:app --host 0.0.0.0 --port 8000 --reload >"$LOGDIR/backend.log" 2>&1 &
backend_pid=$!
children="$children $backend_pid"
echo "[start_dev] backend pid=$backend_pid (logs: $LOGDIR/backend.log)"

# 3) Wait for health endpoint
echo -n "[start_dev] waiting for backend /health"
ready=0
for i in $(seq 1 30); do
  if curl -sS --max-time 2 http://127.0.0.1:8000/health >/dev/null 2>&1; then
    ready=1
    break
  fi
  echo -n "."
  sleep 1
done
echo
if [ "$ready" -ne 1 ]; then
  echo "[start_dev] backend did not become healthy within timeout. Showing last 200 lines of backend log:" >&2
  tail -n 200 "$LOGDIR/backend.log" || true
  fail "backend not healthy"
fi
echo "[start_dev] backend /health OK"

# Quick end-to-end server check using the bundled client CLI
echo "[start_dev] checking server /generate via backend/gemini_client.py..."
client_resp="$LOGDIR/client_check.out"
python3 -u "$ROOT_DIR/backend/gemini_client.py" --question "What is 2+2?" >"$client_resp" 2>&1
client_exit=$?

sed -n '1,200p' "$client_resp" || true

if [ "$client_exit" -ne 0 ]; then
  echo "[start_dev] gemini_client check failed (exit $client_exit). See $client_resp and $LOGDIR/backend.log" >&2
  fail "Server functional check failed"
else
  echo "[start_dev] server functional check passed."
fi


# 5) Launch frontend
echo "[start_dev] starting frontend (npm start) ..."
npm --prefix "$ROOT_DIR/frontend" start >"$LOGDIR/frontend.log" 2>&1 &
frontend_pid=$!
children="$children $frontend_pid"
echo "[start_dev] frontend pid=$frontend_pid (logs: $LOGDIR/frontend.log)"

# 6) Print URL to use the app
# Compute a friendly URL for the frontend. If running inside GitHub Codespaces
# we can use the preview domain pattern so the URL opens in your local browser.
if [ -n "${CODESPACE_NAME:-}" ]; then
  # Codespaces exposes previews at: https://<port>-<codespace>.githubpreview.dev
  FRONTEND_URL="https://3000-${CODESPACE_NAME}.githubpreview.dev"
  echo "[start_dev] detected Codespaces (CODESPACE_NAME=$CODESPACE_NAME)."
  echo "[start_dev] open the preview URL or use the Ports tab in Codespaces to open port 3000."
else
  FRONTEND_URL="http://localhost:3000"
fi

echo
echo "Application is ready. Open this URL in your browser:"
echo "  $FRONTEND_URL"
echo
echo "Logs:"
echo "  backend -> $LOGDIR/backend.log"
echo "  frontend -> $LOGDIR/frontend.log"

echo "[start_dev] tailing logs (press Ctrl-C to stop and cleanup)"
# Tail both logs in foreground so script stays alive. Runs until interrupted.
tail -n +1 -f "$LOGDIR/backend.log" "$LOGDIR/frontend.log"
