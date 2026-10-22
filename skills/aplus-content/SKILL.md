---
name: aplus-content
description: Plan and produce Amazon A+ Content (Enhanced Brand Content) — module layout, headline and body copy in the store's language, and module images at the exact sizes (970x600 header, 970x300 overlay, 300x300 and 220x220 tiles) that keep the same product identical across modules. Use when a brand-registered seller asks for A+ content, EBC, A+ Inhalte, contenu A+, A+コンテンツ or 亚马逊A+详情页. Images render through Teruns (teruns.com credits); planning and copy are free.
---

# Amazon A+ Content

Build an A+ page: choose modules, write the copy, and render each module image at its
exact size with the product kept identical across all of them. Copy and planning are
free; each module image costs Teruns credits (2K = 1, 4K = 2; A+ sizes are small, so 2K
is enough). A new account's one free 2K image covers the header module.

Reply in the language the user writes in. Headlines, body copy and any text inside
images use the store's language (`references/platform-rules.md`).
Scripts: `python3 <this-skill-folder>/scripts/...`.

## Workflow

1. **Inputs.** Product photo path, Amazon store, product facts (as in `product.json`
   below), brand colours or logo file if any, and whether the brand has Standard or
   Premium A+.

2. **Plan the page** (free). Default Standard A+ layout:

   | # | Module | Image | Copy you write |
   | --- | --- | --- | --- |
   | 1 | Image header with text | `aplus_header` 970×600 | headline (≤ 8 words) |
   | 2 | Three images and text | 3 × `aplus_tile` 300×300 | 3 titles + 1–2 lines each |
   | 3 | Image with text overlay | `aplus_overlay` 970×300 | one line (≤ 10 words) |
   | 4 | Four images and text | 4 × `aplus_tile` 220×220 | 4 titles + 1 line each |

   That is 9 images = 9 credits at 2K. Offer a smaller page (modules 1–3, 5 credits).
   Confirm module sizes in the user's A+ Content Manager; they occasionally change.

3. **Write the copy** in the store's language and show it with the plan. Prefer text in
   the module's text fields over text inside images (it reads better on phones and is
   indexed). Only confirmed facts; no superlatives Amazon may reject ("best", "#1"),
   no prices, promotions, reviews or competitor names.

4. **Confirm cost**, check `scripts/teruns_client.py balance`, log in if exit 2
   (`login --start --skill aplus-content`, then `login --wait`).

5. **Render** the header first and get approval; then the rest, attaching the original
   photo and the approved header as references for consistency:

   ```
   python3 scripts/teruns_client.py generate --skill aplus-content \
     --slot aplus_header --marketplace amazon.com --locale en-US \
     --size 2K --aspect 97:60 --output-size 970x600 \
     --ref photo.jpg --prompt-file teruns-output/<slug>/prompts/aplus-01-header.txt \
     --product-file teruns-output/<slug>/product.json \
     --out teruns-output/<slug>/aplus/01-header-970x600.png
   ```

   Aspect / size per module: header `97:60` 970x600 · overlay `97:30` 970x300 ·
   tile `1:1` 300x300 or 220x220.

6. **Check** (free): `python3 scripts/audit_images.py teruns-output/<slug>/aplus --marketplace aplus`.
   It confirms each file matches a module size, is JPEG/PNG and under 2 MB. Look at each
   image for product consistency and spelling.

7. **Deliver** a table: module → file → headline/body copy to paste, plus credits used.

`product.json` fields: name, brand, color, material, dimensions, included,
selling_points, visible_text_on_product, audience, category.

Exit codes from `teruns_client.py`: 0 ok · 2 login · 3 not enough credits (show
`checkout_url`, rerun with the printed `--request-id` after payment) · 1 error.
Never ask for payment details in chat.
