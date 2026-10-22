#!/usr/bin/env python3
"""Copy files from shared/ into each skill so every skill installs on its own.

  python3 tools/sync_shared.py          # write copies
  python3 tools/sync_shared.py --check  # exit 1 if any copy is out of date (CI)
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"

# skill -> files it needs (source in shared/, destination inside the skill)
NEEDS = {
    "listing-image-set": [("teruns_client.py", "scripts"), ("audit_images.py", "scripts"),
                          ("platform-rules.md", "references"), ("prompt-patterns.md", "references")],
    "amazon-main-image": [("teruns_client.py", "scripts"), ("audit_images.py", "scripts"),
                          ("platform-rules.md", "references"), ("prompt-patterns.md", "references")],
    "aplus-content": [("teruns_client.py", "scripts"), ("audit_images.py", "scripts"),
                      ("platform-rules.md", "references"), ("prompt-patterns.md", "references")],
    "listing-image-audit": [("audit_images.py", "scripts"), ("platform-rules.md", "references")],
}


def main() -> None:
    check = "--check" in sys.argv
    stale = []
    for skill, files in NEEDS.items():
        for name, sub in files:
            src = SHARED / name
            dst = ROOT / "skills" / skill / sub / name
            if check:
                if not dst.exists() or dst.read_bytes() != src.read_bytes():
                    stale.append(str(dst.relative_to(ROOT)))
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
            if name.endswith(".py"):
                dst.chmod(0o755)
    if check and stale:
        print("Out of date, run tools/sync_shared.py:\n  " + "\n  ".join(stale))
        sys.exit(1)
    print("shared files " + ("up to date" if check else "synced"))


if __name__ == "__main__":
    main()
