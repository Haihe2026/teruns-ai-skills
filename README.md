# Teruns AI Skills · Listing Studio

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Turn one real product photo into marketplace-compliant listing images — Amazon, Shopify,
TikTok Shop and Etsy — inside Claude Code, Codex, Cursor or any agent that reads `SKILL.md`.
2K or 4K output, with text in your store's language.

| Skill | What it does | Cost |
| --- | --- | --- |
| [`listing-image-audit`](skills/listing-image-audit/SKILL.md) | Checks your existing images: size, format, pure-white main background, product fill, transparency, CMYK, missing image types | **Free**, offline |
| [`amazon-main-image`](skills/amazon-main-image/SKILL.md) | One Amazon main image: pure white RGB 255, product about 85% of the frame, no text or props | 1 image |
| [`listing-image-set`](skills/listing-image-set/SKILL.md) | A full set: main, infographic, close-up, lifestyle, size, in-the-box | 5–7 images |
| [`aplus-content`](skills/aplus-content/SKILL.md) | Amazon A+ module images at exact sizes, plus headline and body copy | 5–9 images |
| [`teruns-catalog`](skills/teruns-catalog/SKILL.md) | Helps choose the right skill | Free |

Credits: **2K image = 1 credit, 4K image = 2 credits.** Failed renders are not charged.
Plans: [teruns.com/#pricing](https://teruns.com/#pricing).

## Install

Any agent (skills CLI):

```bash
npx skills add Haihe2026/teruns-ai-skills
npx skills add Haihe2026/teruns-ai-skills --skill listing-image-audit   # just the free checker
```

Claude Code:

```
/plugin marketplace add Haihe2026/teruns-ai-skills
/plugin install teruns-skill-systems@teruns
```

Codex:

```bash
codex plugin marketplace add Haihe2026/teruns-ai-skills
```

Then open `/plugins` and enable **teruns-skill-systems**.

## Try it

> Check the images in ./photos against Amazon's rules.

> Make an Amazon.de listing image set from ./bottle.jpg — 2K.

> Create a white-background Amazon main image from this photo.

## How it works

1. The skill asks for your product photo, store and product facts, and confirms them.
2. It shows the image plan and the credit cost. Nothing renders until you say yes.
3. The first time, it gives you a teruns.com link to connect your account (one click).
4. Images render one by one, main image first, and keep the product identical across the set.
5. The free checker verifies every image before you get the folder.

If you run out of credits, the skill shows a teruns.com checkout link (Stripe or PayPal).
After paying, say "continue" and it picks up where it stopped.

## Privacy and security

- No model API keys in this repository or on your computer. Scripts use only the Python
  standard library and talk to one host: `teruns.com`.
- `listing-image-audit` makes no network calls at all.
- When you render, your reference photo is sent to teruns.com to make your images.
- Your login token is stored at `~/.teruns/credentials.json` (readable only by you) and
  can be revoked from your teruns.com account.
- Payment details are entered only on Stripe or PayPal pages, never in the chat.

See [SECURITY.md](SECURITY.md).

## AI-generated images

Rendered images are marked as AI-generated in their file metadata. Some marketplaces and
the EU AI Act require disclosure of AI-generated images; follow your store's rules. Every
image must show your real product truthfully.

## For developers

```text
shared/                 source of truth for scripts and references
  teruns_client.py      Teruns API client (stdlib only)
  audit_images.py       offline image checker (stdlib; Pillow optional)
  platform-rules.md     marketplace rules with sources
  prompt-patterns.md    prompt blocks per image slot
skills/<name>/          self-contained skills (copies of shared files)
docs/api.md             the Skills API contract teruns.com implements
tools/sync_shared.py    copy shared files into skills (--check in CI)
tools/mock_server.py    local fake API for testing
```

Test locally:

```bash
python3 tools/mock_server.py --credits 5 &
export TERUNS_API_BASE=http://127.0.0.1:8765/api/v1
python3 shared/teruns_client.py login --start && python3 shared/teruns_client.py login --wait
```

## License

[MIT](LICENSE). Rendering runs on the Teruns service and is billed through
[teruns.com](https://teruns.com).
