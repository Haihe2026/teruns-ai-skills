# Security

## What the scripts do

| Script | Network | Files it reads | Files it writes |
| --- | --- | --- | --- |
| `audit_images.py` | none | the images you point it at | none |
| `teruns_client.py` | `https://teruns.com/api/v1` only (or `TERUNS_API_BASE`) | reference photos you pass with `--ref`, prompt and product files you pass | the output image, `~/.teruns/credentials.json` (mode 600), `~/.teruns/pending_login.json` |

Both are plain Python using only the standard library (Pillow is optional for the audit).
No install scripts, no downloaded binaries, no shell commands, no model API keys.

## Verifying a copy

Each skill folder contains copies of the files in `shared/`. CI runs
`python3 tools/sync_shared.py --check`, so a skill's scripts always match `shared/`.
Releases are tagged; install a tag (`Haihe2026/teruns-ai-skills@v0.2.0`) to pin a version.

## Reporting a problem

Open a private security advisory on this repository (Security → Report a vulnerability).
Please do not open a public issue for a vulnerability.
