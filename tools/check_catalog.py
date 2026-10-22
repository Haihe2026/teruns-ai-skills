#!/usr/bin/env python3
"""catalog.json must list every public skill (except teruns-catalog) exactly once, with complete fields.

teruns.com builds its product pages from this file, so a skill missing here never goes on sale,
and a product left here after its skill is deleted would sell something that no longer exists.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ("en", "de", "fr", "ja", "zh")
INTERNAL = {"teruns-catalog"}

cat = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
errors = []
skills = {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists()} - INTERNAL
slugs = [p["slug"] for p in cat["products"]]

for s in sorted(skills - set(slugs)):
    errors.append(f"skill '{s}' has no product in catalog.json")
for s in sorted(set(slugs) - skills):
    errors.append(f"product '{s}' has no skills/{s}/SKILL.md")
for s in {x for x in slugs if slugs.count(x) > 1}:
    errors.append(f"product '{s}' listed more than once")

for p in cat["products"]:
    s = p["slug"]
    if not re.fullmatch(r"[a-z0-9-]+", s):
        errors.append(f"{s}: slug must be lowercase letters, digits and hyphens")
    if p.get("path") != f"skills/{s}":
        errors.append(f"{s}: path should be skills/{s}")
    if p.get("product_url") != f"https://teruns.com/skills/{s}":
        errors.append(f"{s}: product_url should be https://teruns.com/skills/{s}")
    want_checkout = f"https://teruns.com/checkout?ref={s}" if p.get("paid") else None
    if p.get("checkout_url") != want_checkout:
        errors.append(f"{s}: checkout_url should be {want_checkout}")
    if not p.get("install", "").endswith(f"--skill {s}"):
        errors.append(f"{s}: install command should end with --skill {s}")
    for field in ("name", "summary"):
        missing = [l for l in LANGS if not p.get(field, {}).get(l)]
        if missing:
            errors.append(f"{s}: {field} missing languages {missing}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", p.get("version", "")):
        errors.append(f"{s}: version must look like 1.2.3")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"catalog ok: {len(slugs)} products")
