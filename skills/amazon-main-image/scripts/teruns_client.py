#!/usr/bin/env python3
"""Teruns API client for Teruns AI Skills.

Standard library only. The agent calls this script; it never holds a model API key.
Every command prints exactly one JSON object on stdout so the agent can parse it.

Exit codes:
  0  ok
  1  error (see "error" in the JSON)
  2  login required -> run `login --start`, show verify_url to the user
  3  not enough credits -> show checkout_url to the user

Environment:
  TERUNS_API_BASE  default https://teruns.com/api/v1
  TERUNS_HOME      default ~/.teruns  (credentials.json is stored here, mode 600)

This file is copied into each skill's scripts/ folder by tools/sync_shared.py.
Edit shared/teruns_client.py, never the copies.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request
import uuid

CLIENT_VERSION = "0.2.0"
DEFAULT_BASE = "https://teruns.com/api/v1"
MAX_REF_BYTES = 15 * 1024 * 1024
SIZES = ("2K", "4K")


def api_base() -> str:
    return os.environ.get("TERUNS_API_BASE", DEFAULT_BASE).rstrip("/")


def home() -> pathlib.Path:
    return pathlib.Path(os.environ.get("TERUNS_HOME", pathlib.Path.home() / ".teruns"))


def cred_path() -> pathlib.Path:
    return home() / "credentials.json"


def out(obj: dict, code: int = 0) -> None:
    print(json.dumps(obj, ensure_ascii=False))
    sys.exit(code)


def load_token() -> str | None:
    p = cred_path()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("access_token")
    except (OSError, ValueError):
        return None


def save_token(data: dict) -> None:
    h = home()
    h.mkdir(parents=True, exist_ok=True)
    p = cred_path()
    p.write_text(json.dumps(data))
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass


def request(method: str, path: str, body: dict | None = None, auth: bool = True,
            idempotency_key: str | None = None, timeout: int = 300) -> tuple[int, dict]:
    headers = {
        "Accept": "application/json",
        "User-Agent": f"teruns-skills/{CLIENT_VERSION}",
        "X-Teruns-Client": f"skills/{CLIENT_VERSION}",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if auth:
        token = load_token()
        if not token:
            return 401, {"error": "login_required"}
        headers["Authorization"] = f"Bearer {token}"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    req = urllib.request.Request(api_base() + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            payload = json.loads(raw) if raw else {}
        except ValueError:
            payload = {"error": "http_error", "detail": raw[:300].decode("utf-8", "replace")}
        return e.code, payload
    except urllib.error.URLError as e:
        return 0, {"error": "network_error", "detail": str(e.reason)}


def handle_common(status: int, payload: dict, extra: dict | None = None) -> None:
    """Exit for statuses every command treats the same way."""
    extra = extra or {}
    if status == 401:
        out({"status": "login_required",
             "next": "run: teruns_client.py login --start", **extra}, 2)
    if status == 402:
        out({"status": "insufficient_credits",
             "checkout_url": payload.get("checkout_url", "https://teruns.com/#pricing"),
             "credits_needed": payload.get("credits_needed"),
             "credits_left": payload.get("credits_left"), **extra}, 3)
    if status == 0 or status >= 400:
        out({"status": "error", "http_status": status,
             "error": payload.get("error", "unknown"), "detail": payload.get("detail"),
             **extra}, 1)


# ---------------------------------------------------------------- commands

def cmd_login(a: argparse.Namespace) -> None:
    if a.start:
        status, p = request("POST", "/device/start", {"client": "teruns-skills",
                                                      "client_version": CLIENT_VERSION,
                                                      "skill": a.skill}, auth=False)
        handle_common(status, p)
        state = {"device_code": p["device_code"], "interval": p.get("interval", 3),
                 "expires_at": time.time() + p.get("expires_in", 600)}
        home().mkdir(parents=True, exist_ok=True)
        (home() / "pending_login.json").write_text(json.dumps(state))
        out({"status": "verify_in_browser", "verify_url": p["verify_url"],
             "user_code": p.get("user_code"),
             "next": "show verify_url to the user, then run: teruns_client.py login --wait"})

    pending = home() / "pending_login.json"
    if not pending.exists():
        out({"status": "error", "error": "no_pending_login",
             "next": "run: teruns_client.py login --start"}, 1)
    state = json.loads(pending.read_text())
    deadline = min(state["expires_at"], time.time() + a.timeout)
    while time.time() < deadline:
        status, p = request("POST", "/device/token", {"device_code": state["device_code"]},
                            auth=False)
        if status == 200 and p.get("access_token"):
            save_token({"access_token": p["access_token"], "account": p.get("account"),
                        "saved_at": int(time.time())})
            pending.unlink(missing_ok=True)
            out({"status": "logged_in", "account": p.get("account"),
                 "credits": p.get("credits")})
        if status in (400, 410) and p.get("error") in ("expired_token", "access_denied"):
            pending.unlink(missing_ok=True)
            out({"status": "error", "error": p["error"],
                 "next": "run: teruns_client.py login --start"}, 1)
        if status not in (200, 428) and p.get("error") != "authorization_pending":
            handle_common(status, p)
        time.sleep(max(1, int(state.get("interval", 3))))
    out({"status": "still_pending",
         "next": "the user has not approved yet; run: teruns_client.py login --wait"}, 2)


def cmd_logout(_: argparse.Namespace) -> None:
    cred_path().unlink(missing_ok=True)
    out({"status": "logged_out"})


def cmd_balance(_: argparse.Namespace) -> None:
    status, p = request("GET", "/balance")
    handle_common(status, p)
    out({"status": "ok", "credits": p.get("credits"), "plan": p.get("plan"),
         "renews_at": p.get("renews_at"), "pricing_url": p.get("pricing_url")})


def encode_ref(path: str) -> dict:
    fp = pathlib.Path(path).expanduser()
    if not fp.is_file():
        out({"status": "error", "error": "reference_not_found", "detail": str(fp)}, 1)
    raw = fp.read_bytes()
    if len(raw) > MAX_REF_BYTES:
        out({"status": "error", "error": "reference_too_large",
             "detail": f"{fp.name} is over {MAX_REF_BYTES // (1024 * 1024)} MB"}, 1)
    return {"filename": fp.name, "data": base64.b64encode(raw).decode()}


def parse_px(s: str | None) -> list[int] | None:
    if not s:
        return None
    try:
        w, h = s.lower().split("x")
        return [int(w), int(h)]
    except ValueError:
        out({"status": "error", "error": "bad_output_size", "detail": s}, 1)
    return None


def cmd_generate(a: argparse.Namespace) -> None:
    prompt = a.prompt
    if a.prompt_file:
        prompt = pathlib.Path(a.prompt_file).expanduser().read_text(encoding="utf-8")
    if not prompt:
        out({"status": "error", "error": "prompt_required"}, 1)
    product = {}
    if a.product_file:
        product = json.loads(pathlib.Path(a.product_file).expanduser().read_text(encoding="utf-8"))
    body = {
        "skill": a.skill,
        "slot": a.slot,
        "marketplace": a.marketplace,
        "locale": a.locale,
        "size": a.size,
        "aspect": a.aspect,
        "output_size": parse_px(a.output_size),
        "prompt": prompt,
        "product": product,
        "reference_images": [encode_ref(r) for r in a.ref],
        "client_version": CLIENT_VERSION,
    }
    key = a.request_id or str(uuid.uuid4())
    status, p = request("POST", "/images/generate", body, idempotency_key=key, timeout=a.timeout)
    handle_common(status, p, {"request_id": key,
                              "retry": "after fixing, rerun the same command with --request-id " + key})

    images = p.get("images") or []
    if not images:
        out({"status": "error", "error": "no_image_returned", "request_id": key}, 1)
    dest = pathlib.Path(a.out).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    img = images[0]
    if img.get("b64"):
        dest.write_bytes(base64.b64decode(img["b64"]))
    elif img.get("url"):
        try:
            with urllib.request.urlopen(img["url"], timeout=120) as r:
                dest.write_bytes(r.read())
        except urllib.error.URLError as e:
            out({"status": "error", "error": "download_failed", "detail": str(e),
                 "request_id": key, "image_url": img["url"]}, 1)
    else:
        out({"status": "error", "error": "no_image_payload", "request_id": key}, 1)
    out({"status": "ok", "file": str(dest), "width": img.get("width"),
         "height": img.get("height"), "credits_charged": p.get("credits_charged"),
         "credits_left": p.get("credits_left"), "request_id": key})


def main() -> None:
    ap = argparse.ArgumentParser(description="Teruns API client for Teruns AI Skills")
    sub = ap.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("login", help="link this computer to a teruns.com account")
    g = lg.add_mutually_exclusive_group(required=True)
    g.add_argument("--start", action="store_true", help="get a browser link for the user")
    g.add_argument("--wait", action="store_true", help="wait for the user to approve")
    lg.add_argument("--skill", default="unknown")
    lg.add_argument("--timeout", type=int, default=120, help="seconds to wait (with --wait)")
    lg.set_defaults(func=cmd_login)

    sub.add_parser("logout").set_defaults(func=cmd_logout)
    sub.add_parser("balance").set_defaults(func=cmd_balance)

    gen = sub.add_parser("generate", help="render one image (charges credits)")
    gen.add_argument("--skill", required=True)
    gen.add_argument("--slot", required=True, help="e.g. amazon_main, lifestyle, aplus_header")
    gen.add_argument("--marketplace", required=True, help="e.g. amazon.com, amazon.de, shopify")
    gen.add_argument("--locale", required=True, help="language of any text in the image, e.g. de-DE")
    gen.add_argument("--size", choices=SIZES, default="2K")
    gen.add_argument("--aspect", default="1:1")
    gen.add_argument("--output-size", help="exact final pixels, e.g. 970x600")
    gen.add_argument("--ref", action="append", default=[], help="reference photo path (repeatable)")
    gen.add_argument("--prompt")
    gen.add_argument("--prompt-file")
    gen.add_argument("--product-file", help="JSON file with confirmed product facts")
    gen.add_argument("--out", required=True, help="where to save the image")
    gen.add_argument("--request-id", help="reuse to retry without being charged twice")
    gen.add_argument("--timeout", type=int, default=300)
    gen.set_defaults(func=cmd_generate)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
