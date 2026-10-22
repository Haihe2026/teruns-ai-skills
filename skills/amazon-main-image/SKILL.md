---
name: amazon-main-image
description: Create or fix an Amazon main image from a real product photo — pure white RGB 255 background, product filling about 85% of the frame, no text, props or badges — in 2K or 4K, then verify it with an offline check. Use when a seller needs a compliant Amazon main image, white-background product photo, Hauptbild, image principale, メイン画像 or 亚马逊白底主图, or when an existing main image was rejected. Renders through Teruns (teruns.com credits).
---

# Amazon Main Image

Produce one Amazon-compliant main image from the user's product photo, or replace a main
image that fails Amazon's rules. Rendering costs Teruns credits (2K = 1, 4K = 2).
Checking is free and offline.

Reply in the language the user writes in. Scripts are in this skill's folder:
`python3 <this-skill-folder>/scripts/...`.

## Workflow

1. **Inputs.** Product photo path (required), Amazon store (amazon.com, amazon.de, …),
   2K or 4K (default 2K). Ask for the printed text visible on the product so it can be
   kept exact; list it in `visible_text_on_product`.

2. **If the user already has a main image, check it first (free):**

   ```
   python3 scripts/audit_images.py current-main.jpg --marketplace amazon.com --main current-main.jpg
   ```

   Then look at the image yourself for what the script cannot see: text or logos added
   around the product, props, hands, packaging, watermarks, inset images, a drawing
   instead of a photo. If it passes, say so and stop — no credits needed.

3. **Confirm cost.** "1 image × 1 credit (2K)". Get a clear yes.

4. **Account.** Run `scripts/teruns_client.py balance`. Exit 2 → `login --start
   --skill amazon-main-image`, show `verify_url` and `user_code`, then `login --wait`.

5. **Render.** Write the prompt from `references/prompt-patterns.md`
   (identity lock + `amazon_main` scene + "no text" rule + safety rule) to a file, then:

   ```
   python3 scripts/teruns_client.py generate --skill amazon-main-image \
     --slot amazon_main --marketplace amazon.com --locale en-US \
     --size 2K --aspect 1:1 --output-size 2000x2000 \
     --ref /path/to/photo.jpg --prompt-file teruns-output/<slug>/prompts/main.txt \
     --out teruns-output/<slug>/amazon.com/01-amazon_main.png
   ```

   4K: `--size 4K --output-size 4000x4000`.

6. **Verify.** Run `audit_images.py` on the result and look at it beside the original
   photo: same shape, colour, parts and printed text. If the background is not pure
   white or the fill is under about 85%, explain and offer one re-render with the
   scene block made stricter (it costs a credit again).

7. **Deliver** the file path, the check result and credits left.

Exit codes from `teruns_client.py`: 0 ok · 2 login needed · 3 not enough credits (show
`checkout_url`; after the user pays, rerun with the `--request-id` from the output) ·
1 error (retry once with the same `--request-id`). Never ask for payment details in chat.

## Amazon main image rules used here

See `references/platform-rules.md`. In short: pure white RGB 255,255,255 background;
product about 85% of the frame; only the product being sold; no text, logos (other than
on the product), watermarks, borders, badges, props or inset images; realistic photo of
the real product; 500–10,000 px on the longest side, over 1,000 px for zoom.
