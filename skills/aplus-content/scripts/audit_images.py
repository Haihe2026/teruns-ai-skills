#!/usr/bin/env python3
"""Check product images against marketplace rules. Runs fully offline; sends nothing anywhere.

Usage:
  audit_images.py <file-or-folder> [...] --marketplace amazon.com [--main FILE] [--json]
  audit_images.py <folder> --marketplace aplus

Marketplaces: amazon(.com/.de/.co.jp/...), shopify, etsy, tiktok, aplus
Size, format and file-size checks need only Python. Pixel checks (white background,
how much of the frame the product fills) work on PNG with plain Python and on JPEG/WebP
when Pillow is installed (pip install pillow). What a script cannot see — text, logos,
props, watermarks, wrong colours — the agent checks by looking at each image.

This file is copied into each skill's scripts/ folder by tools/sync_shared.py.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import struct
import sys
import zlib

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff"}

RULES = {
    "amazon": {"min_long": 500, "max_long": 10000, "zoom_long": 1000, "rec_long": 2000,
               "formats": {"jpeg", "png", "gif", "tiff"}, "main_white": True,
               "main_fill": 0.85, "rec_count": 7, "max_mb": None},
    "shopify": {"min_long": 1, "max_long": 5000, "max_mp": 25, "rec_long": 2048,
                "formats": {"jpeg", "png", "gif", "tiff", "webp"}, "max_mb": 20},
    "etsy": {"min_both": 635, "rec_long": 2000, "formats": {"jpeg", "png", "gif"},
             "max_mb": 1, "no_alpha": True},
    "tiktok": {"min_both": 600, "rec_long": 800, "formats": {"jpeg", "png", "webp"},
               "max_count": 9, "rec_count": 5, "max_mb": None, "reported": True},
    "aplus": {"formats": {"jpeg", "png"}, "max_mb": 2,
              "sizes": {(970, 600): "Image header with text", (970, 300): "Image with text overlay",
                        (300, 300): "Three images / single image and sidebar",
                        (220, 220): "Four images and text", (600, 180): "Company logo"},
              "max_width": 1464},
}


# ------------------------------------------------------------------ header parsing

def read_header(p: pathlib.Path) -> dict:
    b = p.read_bytes()
    info = {"bytes": len(b), "format": None, "width": None, "height": None, "mode": None}
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h, depth, ctype = struct.unpack(">IIBB", b[16:26])
        info.update(format="png", width=w, height=h,
                    mode={0: "L", 2: "RGB", 3: "P", 4: "LA", 6: "RGBA"}.get(ctype, "?"),
                    bit_depth=depth)
    elif b[:3] == b"\xff\xd8\xff":
        info["format"] = "jpeg"
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF:
                i += 1
                continue
            m = b[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                comps = b[i + 9]
                info.update(width=w, height=h, mode={1: "L", 3: "RGB", 4: "CMYK"}.get(comps, "?"))
                break
            if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                i += 2
                continue
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    elif b[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", b[6:10])
        info.update(format="gif", width=w, height=h, animated=b.count(b"\x21\xf9\x04") > 1)
    elif b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        info["format"] = "webp"
        kind = b[12:16]
        if kind == b"VP8X":
            info.update(width=1 + int.from_bytes(b[24:27], "little"),
                        height=1 + int.from_bytes(b[27:30], "little"))
        elif kind == b"VP8L":
            v = int.from_bytes(b[21:25], "little")
            info.update(width=(v & 0x3FFF) + 1, height=((v >> 14) & 0x3FFF) + 1)
        elif kind == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            info.update(width=w & 0x3FFF, height=h & 0x3FFF)
    elif b[:4] in (b"II*\x00", b"MM\x00*"):
        info["format"] = "tiff"
    return info


# ------------------------------------------------------------------ pixel access

def png_pixels(p: pathlib.Path):
    """Decode 8-bit non-interlaced PNG to (w, h, channels, rows). None if unsupported."""
    b = p.read_bytes()
    pos, idat, w = 8, b"", 0
    while pos < len(b):
        n = struct.unpack(">I", b[pos:pos + 4])[0]
        t = b[pos + 4:pos + 8]
        d = b[pos + 8:pos + 8 + n]
        if t == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", d)
            if depth != 8 or interlace or ctype not in (0, 2, 4, 6):
                return None
            ch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
        elif t == b"IDAT":
            idat += d
        elif t == b"IEND":
            break
        pos += 12 + n
    raw = zlib.decompress(idat)
    stride = w * ch
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[i]
        cur = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = cur[x - ch] if x >= ch else 0
            up = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1:
                cur[x] = (cur[x] + a) & 255
            elif f == 2:
                cur[x] = (cur[x] + up) & 255
            elif f == 3:
                cur[x] = (cur[x] + (a + up) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(up - c), abs(a - c), abs(a + up - 2 * c)
                pr = a if pa <= pb and pa <= pc else (up if pb <= pc else c)
                cur[x] = (cur[x] + pr) & 255
        rows.append(cur)
        prev = cur
    return w, h, ch, rows


def load_rgb(p: pathlib.Path, fmt: str):
    """Return (w, h, get(x, y) -> (r, g, b, a)) or None if pixels are unavailable."""
    try:
        from PIL import Image  # type: ignore
        im = Image.open(p)
        im.seek(0)
        im = im.convert("RGBA")
        w, h = im.size
        if max(w, h) > 1200:  # sample a smaller copy; enough for edge and fill checks
            s = 1200 / max(w, h)
            im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.NEAREST)
            w, h = im.size
        px = im.load()
        return w, h, lambda x, y: px[x, y]
    except ImportError:
        pass
    except Exception:
        return None
    if fmt == "png":
        try:
            dec = png_pixels(p)
        except Exception:
            dec = None
        if not dec:
            return None
        w, h, ch, rows = dec

        def get(x, y):
            r = rows[y]
            o = x * ch
            if ch == 1:
                return r[o], r[o], r[o], 255
            if ch == 2:
                return r[o], r[o], r[o], r[o + 1]
            if ch == 3:
                return r[o], r[o + 1], r[o + 2], 255
            return r[o], r[o + 1], r[o + 2], r[o + 3]
        return w, h, get
    return None


def pixel_stats(w, h, get) -> dict:
    step = max(1, max(w, h) // 600)
    band = max(1, int(min(w, h) * 0.02))
    edge = pure = near = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            if x < band or y < band or x >= w - band or y >= h - band:
                r, g, b, a = get(x, y)
                edge += 1
                if a == 255 and r == g == b == 255:
                    pure += 1
                elif a == 255 and min(r, g, b) >= 245:
                    near += 1
    x0, y0, x1, y1 = w, h, -1, -1
    alpha = False
    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b, a = get(x, y)
            if a < 255:
                alpha = True
            if a > 0 and min(r, g, b) < 245:
                x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
    if x1 < 0:
        fill, touches = 0.0, False
    else:
        bw, bh = x1 - x0 + step, y1 - y0 + step
        fill = max(bw / w, bh / h)
        touches = x0 <= step or y0 <= step or x1 >= w - 1 - step or y1 >= h - 1 - step
    return {"edge_pure_white": pure / edge if edge else 0, "edge_near_white": near / edge if edge else 0,
            "fill": round(min(fill, 1.0), 3), "touches_edge": touches, "has_transparency": alpha}


# ------------------------------------------------------------------ checks

def norm_market(m: str) -> str:
    m = m.lower()
    if m.startswith("amazon"):
        return "amazon"
    if "a+" in m or m in ("aplus", "a-plus"):
        return "aplus"
    if m.startswith("tiktok"):
        return "tiktok"
    return m


def check_file(p: pathlib.Path, market: str, is_main: bool) -> dict:
    r = RULES[market]
    info = read_header(p)
    f = []  # (level, message)

    def add(level, msg):
        f.append({"level": level, "message": msg})

    fmt, w, h, mb = info["format"], info["width"], info["height"], info["bytes"] / 1048576
    if fmt not in r["formats"]:
        add("FAIL", f"format {fmt or 'unknown'} not accepted (use {', '.join(sorted(r['formats']))})")
    if info.get("animated"):
        add("FAIL", "animated GIF not accepted")
    if info.get("mode") == "CMYK":
        add("FAIL", "CMYK colour; convert to sRGB/RGB")
    if r.get("max_mb") and mb > r["max_mb"]:
        add("FAIL" if market == "shopify" else "WARN", f"file is {mb:.1f} MB (limit {r['max_mb']} MB)")
    if w and h:
        long_side = max(w, h)
        if "min_long" in r and long_side < r["min_long"]:
            add("FAIL", f"{w}x{h}: longest side under {r['min_long']} px")
        if "max_long" in r and long_side > r["max_long"]:
            add("FAIL", f"{w}x{h}: longest side over {r['max_long']} px")
        if "max_mp" in r and w * h > r["max_mp"] * 1_000_000:
            add("FAIL", f"{w}x{h}: over {r['max_mp']} megapixels")
        if "min_both" in r and min(w, h) < r["min_both"]:
            add("FAIL" if market == "etsy" and is_main else "WARN",
                f"{w}x{h}: under {r['min_both']} x {r['min_both']} px")
        if "zoom_long" in r and long_side <= r["zoom_long"]:
            add("WARN", f"{w}x{h}: zoom needs more than {r['zoom_long']} px on the longest side")
        if "rec_long" in r and long_side < r["rec_long"]:
            add("INFO", f"{w}x{h}: {r['rec_long']} px or more recommended")
        if market == "aplus":
            if (w, h) in r["sizes"]:
                add("OK", f"{w}x{h} matches A+ module: {r['sizes'][(w, h)]}")
            elif w > r["max_width"]:
                add("FAIL", f"{w}x{h}: wider than {r['max_width']} px")
            else:
                add("WARN", f"{w}x{h} does not match a standard A+ module size")
    elif fmt != "tiff":
        add("WARN", "could not read image size")

    need_pixels = (is_main and r.get("main_white")) or r.get("no_alpha")
    if need_pixels:
        px = load_rgb(p, fmt or "")
        if not px:
            add("INFO", "pixel checks skipped (install Pillow to check JPEG/WebP backgrounds)")
        else:
            s = pixel_stats(*px)
            info["pixels"] = s
            if r.get("no_alpha") and s["has_transparency"]:
                add("FAIL", "transparent areas (Etsy shows them as black)")
            if is_main and r.get("main_white"):
                if s["has_transparency"]:
                    add("FAIL", "main image has transparency; flatten onto pure white")
                if s["edge_pure_white"] >= 0.98:
                    add("OK", "background is pure white (RGB 255,255,255)")
                elif s["edge_pure_white"] + s["edge_near_white"] >= 0.98:
                    add("FAIL", "background is near-white, not pure RGB 255,255,255")
                else:
                    add("FAIL", "background is not white")
                need = r["main_fill"]
                if s["fill"] >= need:
                    add("OK", f"product fills {s['fill']:.0%} of the frame")
                else:
                    add("WARN", f"product fills {s['fill']:.0%} of the frame (aim for about {need:.0%})")
                if s["touches_edge"]:
                    add("WARN", "product touches the image edge; it may be cropped")
    return {"file": str(p), "main": is_main, "info": info, "findings": f,
            "result": "FAIL" if any(x["level"] == "FAIL" for x in f)
            else "WARN" if any(x["level"] == "WARN" for x in f) else "OK"}


def collect(paths: list[str]) -> list[pathlib.Path]:
    files = []
    for s in paths:
        p = pathlib.Path(s).expanduser()
        if p.is_dir():
            files += sorted(x for x in p.iterdir() if x.suffix.lower() in IMAGE_EXT)
        elif p.is_file():
            files.append(p)
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--marketplace", required=True)
    ap.add_argument("--main", help="file that is the main image (default: first in name order)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    market = norm_market(a.marketplace)
    if market not in RULES:
        print(json.dumps({"status": "error", "error": f"unknown marketplace {a.marketplace}",
                          "supported": sorted(RULES)}))
        sys.exit(1)
    files = collect(a.paths)
    if not files:
        print(json.dumps({"status": "error", "error": "no images found"}))
        sys.exit(1)
    main_file = pathlib.Path(a.main).expanduser() if a.main else files[0]
    results = [check_file(f, market, market != "aplus" and f.resolve() == main_file.resolve())
               for f in files]

    set_notes = []
    r = RULES[market]
    if r.get("rec_count") and len(files) < r["rec_count"]:
        set_notes.append({"level": "WARN", "message":
                          f"{len(files)} images; {r['rec_count']} or more recommended"})
    if r.get("max_count") and len(files) > r["max_count"]:
        set_notes.append({"level": "WARN", "message": f"{len(files)} images; at most {r['max_count']} shown"})
    if r.get("reported"):
        set_notes.append({"level": "INFO", "message":
                          "TikTok Shop limits here come from seller guides, not official docs"})

    report = {"status": "ok", "marketplace": a.marketplace, "rules": market,
              "images": results, "set": set_notes,
              "summary": {k: sum(1 for x in results if x["result"] == k) for k in ("OK", "WARN", "FAIL")}}
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    for x in results:
        tag = " (main)" if x["main"] else ""
        i = x["info"]
        print(f"[{x['result']}] {pathlib.Path(x['file']).name}{tag}  "
              f"{i.get('width')}x{i.get('height')} {i.get('format')} {i['bytes'] / 1024:.0f} KB")
        for g in x["findings"]:
            print(f"    {g['level']:4}  {g['message']}")
    for g in set_notes:
        print(f"[SET] {g['level']}  {g['message']}")
    s = report["summary"]
    print(f"\n{s['OK']} OK, {s['WARN']} warning, {s['FAIL']} failing")


if __name__ == "__main__":
    main()
