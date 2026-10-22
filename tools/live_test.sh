#!/usr/bin/env bash
# Test the live teruns.com Skills API (docs/api.md) from your own computer.
#
#   bash tools/live_test.sh                  # API checks + device login + balance (free)
#   bash tools/live_test.sh photo.jpg        # also renders 1 image (uses the free 2K trial or 1 credit)
#
# Uses a temporary login folder, so your real ~/.teruns is not touched.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${TERUNS_API_BASE:-https://teruns.com/api/v1}"
export TERUNS_API_BASE="$BASE" TERUNS_HOME="$(mktemp -d)"
C="python3 $ROOT/shared/teruns_client.py"
A="python3 $ROOT/shared/audit_images.py"
PHOTO="${1:-}"
pass=0; fail=0
ok()  { echo "PASS  $1"; pass=$((pass+1)); }
bad() { echo "FAIL  $1"; echo "      $2"; fail=$((fail+1)); }
field() { python3 -c "import json,sys;d=json.loads(sys.argv[1]);print(d.get('$2',''))" "$1" 2>/dev/null; }

probe() { # method path body expected_status label
  local out code
  out=$(curl -s -m 30 -w '\n%{http_code}' -X "$1" -H 'Content-Type: application/json' -d "$3" "$BASE$2")
  code=$(tail -n1 <<<"$out"); body=$(sed '$d' <<<"$out")
  if [[ " $4 " == *" $code "* ]] && python3 -c "import json,sys;json.loads(sys.argv[1])" "$body" 2>/dev/null; then
    ok "$5 -> $code"
  else
    bad "$5 (expected $4, got $code)" "${body:0:200}"
  fi
}

echo "Testing $BASE"
probe GET  /balance         '{}'                      "401"     "balance without login"
probe POST /images/generate '{}'                      "401"     "generate without login"
probe POST /device/token    '{"device_code":"bogus"}' "400 410" "device/token with an unknown code"

r=$($C login --start --skill live-test); rc=$?
url=$(field "$r" verify_url); codeu=$(field "$r" user_code)
if [ $rc -eq 0 ] && [ -n "$url" ]; then ok "device/start returns verify_url"; else bad "device/start" "$r"; fi

if [ -n "$url" ]; then
  echo
  echo ">>> Open this link, sign in and approve (code $codeu):"
  echo ">>> $url"
  echo ">>> Waiting up to 5 minutes..."
  r=$($C login --wait --timeout 300); rc=$?
  if [ $rc -eq 0 ]; then ok "device login approved ($(field "$r" account))"; else bad "device login" "$r"; fi

  r=$($C balance); rc=$?
  credits=$(field "$r" credits); trial=$(field "$r" trial_images)
  if [ $rc -eq 0 ] && [ -n "$credits" ] && [ -n "$trial" ]; then
    ok "balance: credits=$credits trial_images=$trial"
  else bad "balance has credits and trial_images" "$r"; fi

  if [ -n "$PHOTO" ] && [ $rc -eq 0 ]; then
    OUT="$TERUNS_HOME/out"; P="$TERUNS_HOME/prompt.txt"
    cat > "$P" <<'EOF'
Image 1 is the exact product being sold. Reproduce it faithfully: same shape, colours,
materials, parts and printed text. Single product, centered, on a pure white (#FFFFFF)
seamless background with a soft natural contact shadow, filling about 88% of the frame,
fully in frame, even soft studio lighting. No text, logos, badges, borders, props or hands.
EOF
    G="$C generate --skill live-test --marketplace amazon.com --locale en-US --ref $PHOTO --prompt-file $P"
    if [ "$credits" = "0" ] && [ "$trial" = "1" ]; then
      r=$($G --slot amazon_main --size 4K --out "$OUT/4k.png"); rc=$?
      if [ $rc -eq 3 ] && [ "$(field "$r" reason)" = "trial_2k_only" ]; then ok "4K refused while only the trial is left"
      else bad "4K on trial should be 402 trial_2k_only" "$r"; fi
    fi
    r=$($G --slot amazon_main --size 2K --aspect 1:1 --output-size 2000x2000 --out "$OUT/01-main.png" --request-id live-test-1); rc=$?
    if [ $rc -eq 0 ]; then
      ok "2K render saved: charged=$(field "$r" credits_charged) trial_used=$(field "$r" trial_used)"
      r2=$($G --slot amazon_main --size 2K --aspect 1:1 --output-size 2000x2000 --out "$OUT/01-again.png" --request-id live-test-1)
      if [ "$(field "$r2" credits_left)" = "$(field "$r" credits_left)" ] && [ "$(field "$r2" trial_images_left)" = "$(field "$r" trial_images_left)" ]; then
        ok "same request id is not charged twice"
      else bad "idempotent retry" "$r2"; fi
      echo; $A "$OUT/01-main.png" --marketplace amazon.com; echo
      cp "$OUT/01-main.png" ./teruns-live-test-main.png && echo "Image copied to ./teruns-live-test-main.png"
    else
      bad "2K render" "$r"
    fi
  fi
fi

echo
echo "$pass passed, $fail failed"
rm -rf "$TERUNS_HOME"
