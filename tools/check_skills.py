#!/usr/bin/env python3
"""Check every skills/<name>/SKILL.md: frontmatter present, name matches folder, description length."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []
for skill in sorted((ROOT / "skills").iterdir()):
    md = skill / "SKILL.md"
    if not md.exists():
        errors.append(f"{skill.name}: missing SKILL.md")
        continue
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{skill.name}: no frontmatter")
        continue
    fields = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    name = fields.get("name", "").strip()
    desc = fields.get("description", "").strip()
    if name != skill.name:
        errors.append(f"{skill.name}: name '{name}' does not match folder")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append(f"{skill.name}: name must be lowercase letters, digits, hyphens (max 64)")
    if not desc or len(desc) > 1024:
        errors.append(f"{skill.name}: description missing or over 1024 characters ({len(desc)})")
    if "<" in desc or ">" in desc:
        errors.append(f"{skill.name}: description must not contain angle brackets")
    for ref in re.findall(r"`(scripts/[\w.-]+|references/[\w.-]+)`", text):
        if not (skill / ref).exists():
            errors.append(f"{skill.name}: references missing file {ref}")
    print(f"ok {skill.name} ({len(desc)} chars)" if not errors else "", end="")
    print()
if errors:
    print("\n".join(errors))
    sys.exit(1)
