#!/usr/bin/env python3
"""Local stand-in for the teruns.com Skills API (docs/api.md), for testing only.

Run:  python3 tools/mock_server.py --port 8765 --credits 3
Then: TERUNS_API_BASE=http://127.0.0.1:8765/api/v1 python3 shared/teruns_client.py balance

Device login auto-approves on the second poll. Generated images are a white canvas
with a grey box filling about 88% of the frame (a passing Amazon main image).
"""
from __future__ import annotations

import argparse
import base64
import json
import secrets
import struct
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATE = {"credits": 3, "trial": 1, "devices": {}, "tokens": set(), "idem": {}}


def png(w: int, h: int, fill: float = 0.88) -> bytes:
    bw, bh = int(w * fill), int(h * fill)
    x0, y0 = (w - bw) // 2, (h - bh) // 2
    white, grey = b"\xff\xff\xff", b"\x80\x80\x80"
    rows = []
    blank = b"\x00" + white * w
    boxrow = b"\x00" + white * x0 + grey * bw + white * (w - x0 - bw)
    for y in range(h):
        rows.append(boxrow if y0 <= y < y0 + bh else blank)
    raw = b"".join(rows)

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def send(self, code: int, obj: dict) -> None:
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n)) if n else {}

    def authed(self) -> bool:
        return self.headers.get("Authorization", "").removeprefix("Bearer ") in STATE["tokens"]

    def do_GET(self):
        if self.path == "/api/v1/balance":
            if not self.authed():
                return self.send(401, {"error": "invalid_token"})
            return self.send(200, {"credits": STATE["credits"], "trial_images": STATE["trial"], "plan": "trial",
                                   "renews_at": None, "pricing_url": "https://teruns.com/#pricing"})
        self.send(404, {"error": "not_found"})

    def do_POST(self):
        b = self.body()
        if self.path == "/api/v1/device/start":
            dc = secrets.token_hex(8)
            STATE["devices"][dc] = 0
            return self.send(200, {"device_code": dc, "user_code": "TRNS-0001",
                                   "verify_url": "https://teruns.com/link?code=TRNS-0001",
                                   "interval": 1, "expires_in": 60})
        if self.path == "/api/v1/device/token":
            dc = b.get("device_code")
            if dc not in STATE["devices"]:
                return self.send(410, {"error": "expired_token"})
            STATE["devices"][dc] += 1
            if STATE["devices"][dc] < 2:
                return self.send(428, {"error": "authorization_pending"})
            tok = secrets.token_hex(16)
            STATE["tokens"].add(tok)
            return self.send(200, {"access_token": tok, "account": "t***@example.com",
                                   "credits": STATE["credits"], "trial_images": STATE["trial"]})
        if self.path == "/api/v1/images/generate":
            if not self.authed():
                return self.send(401, {"error": "invalid_token"})
            key = self.headers.get("Idempotency-Key")
            if key in STATE["idem"]:
                return self.send(200, STATE["idem"][key])
            cost = 2 if b.get("size") == "4K" else 1
            use_trial = cost == 1 and STATE["trial"] > 0
            if not use_trial and STATE["credits"] < cost:
                return self.send(402, {"error": "trial_2k_only" if STATE["trial"] else "insufficient_credits",
                                       "credits_needed": cost, "credits_left": STATE["credits"],
                                       "trial_images_left": STATE["trial"],
                                       "checkout_url": f"https://teruns.com/checkout?plan=starter&ref={b.get('skill')}"})
            for f in ("prompt", "slot", "marketplace", "locale"):
                if not b.get(f):
                    return self.send(422, {"error": "missing_field", "detail": f})
            w, h = b.get("output_size") or [256, 256]
            if use_trial:
                STATE["trial"] -= 1
            else:
                STATE["credits"] -= cost
            resp = {"images": [{"b64": base64.b64encode(png(w, h)).decode(), "width": w, "height": h}],
                    "credits_charged": 0 if use_trial else cost, "credits_left": STATE["credits"],
                    "trial_used": use_trial, "trial_images_left": STATE["trial"], "request_id": key}
            STATE["idem"][key] = resp
            return self.send(200, resp)
        self.send(404, {"error": "not_found"})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--credits", type=int, default=3)
    ap.add_argument("--trial", type=int, default=1)
    a = ap.parse_args()
    STATE["credits"] = a.credits
    STATE["trial"] = a.trial
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
