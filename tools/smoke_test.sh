#!/usr/bin/env bash
# End-to-end test of a skill's own script copies against tools/mock_server.py.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
PORT=8765
export TERUNS_API_BASE="http://127.0.0.1:$PORT/api/v1" TERUNS_HOME="$TMP/home"
python3 "$ROOT/tools/mock_server.py" --port $PORT --credits 3 &
PID=$!
trap 'kill $PID; rm -rf "$TMP"' EXIT
sleep 1

C="python3 $ROOT/skills/listing-image-set/scripts/teruns_client.py"
A="python3 $ROOT/skills/listing-image-set/scripts/audit_images.py"
expect() { [ "$1" = "$2" ] || { echo "FAIL: expected exit $2, got $1 ($3)"; exit 1; }; }

set +e
$C balance > /dev/null; expect $? 2 "balance before login"
$C login --start --skill smoke > /dev/null; expect $? 0 "login start"
$C login --wait --timeout 15 > /dev/null; expect $? 0 "login wait"
echo ref > "$TMP/ref.jpg"
G="$C generate --skill smoke --marketplace amazon.com --locale en-US --ref $TMP/ref.jpg --prompt test"
$G --slot amazon_main --output-size 1200x1200 --out "$TMP/out/01-main.png" --request-id r1 > /dev/null; expect $? 0 "render 1"
$G --slot amazon_main --output-size 1200x1200 --out "$TMP/out/01-again.png" --request-id r1 > "$TMP/r.json"; expect $? 0 "idempotent retry"
grep -q '"credits_left": 2' "$TMP/r.json" || { echo "FAIL: retry charged again"; exit 1; }
$G --slot lifestyle --size 4K --out "$TMP/out/02.png" > /dev/null; expect $? 0 "4K render"
$G --slot lifestyle --size 4K --out "$TMP/out/03.png" > "$TMP/r.json"; expect $? 3 "out of credits"
grep -q checkout_url "$TMP/r.json" && grep -q request_id "$TMP/r.json" || { echo "FAIL: 402 output incomplete"; exit 1; }
$A "$TMP/out/01-main.png" --marketplace amazon.com --json > "$TMP/a.json"; expect $? 0 "audit"
set -e
python3 - "$TMP/a.json" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))["images"][0]
assert r["result"] == "OK", r
print("smoke test passed")
EOF
