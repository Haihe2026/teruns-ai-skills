---
name: listing-image-set
description: Turn one real product photo into a full, marketplace-compliant listing image set (main image, infographics, close-ups, lifestyle, size and in-the-box images) for Amazon, Shopify, TikTok Shop or Etsy, in 2K or 4K, with text in the store's language. Use when a seller asks for listing photos, product images, an Amazon image set, Produktbilder, photos produit, 商品画像, 商品图 or 亚马逊套图. Renders through Teruns (teruns.com credits).
---

# Listing Image Set

Make a complete set of listing images from the user's own product photo. You plan the set,
write each prompt, and render through the Teruns API with `scripts/teruns_client.py`.
Rendering costs Teruns credits (2K = 1 credit, 4K = 2 credits per image). Every new
Teruns account gets **one free 2K image**. Planning, checking and fixing prompts cost nothing.

Reply in the language the user writes in. Text drawn inside images follows the store's
language instead (see `references/platform-rules.md`).

Scripts live in this skill's folder. Run them with `python3 <this-skill-folder>/scripts/...`.

## Workflow

### 1. Collect the inputs

Ask only for what is missing, in one message:

- **Product photo(s)**: a local file path. Required. A clear phone photo is enough.
- **Store**: amazon.com / amazon.de / amazon.co.jp / … , shopify, tiktok, or etsy.
  For Shopify, Etsy and TikTok Shop, also ask the selling language (default en-US).
- **Product facts**: name, brand, colour, material, dimensions, what is included,
  and 3–5 selling points.
- **Resolution**: 2K (default) or 4K.

Never invent facts. If the user has no dimensions, skip the size slot rather than guess.

### 2. Confirm the facts and the plan

Write the confirmed facts to `teruns-output/<product-slug>/product.json`:

```json
{
  "name": "", "brand": "", "color": "", "material": "", "dimensions": "",
  "included": [], "selling_points": [], "visible_text_on_product": [],
  "audience": "", "category": ""
}
```

`visible_text_on_product` = every word printed on the real product, copied from the photo.

Then show the plan as a short table: slot, what it shows, text in the image, size.
Use the default plan for the store:

| # | Amazon (7) | Shopify (5) | TikTok Shop (6) | Etsy (5) |
| --- | --- | --- | --- | --- |
| 1 | `amazon_main` 1:1 | main on white or light neutral 1:1 | main on white 1:1 | lifestyle hero 4:3 |
| 2 | `benefit_infographic` | `lifestyle` | `benefit_infographic` | `detail_closeup` 4:3 |
| 3 | `detail_closeup` | `detail_closeup` | `lifestyle` (casual, phone-shot feel) | `lifestyle` 4:3 |
| 4 | `lifestyle` | `lifestyle` (second scene) | `detail_closeup` | `size_dimensions` 4:3 |
| 5 | `size_dimensions` | `size_dimensions` | `size_dimensions` | `in_the_box` 4:3 |
| 6 | `lifestyle` (second scene) or `comparison` | | `in_the_box` | |
| 7 | `in_the_box` | | | |

State the total cost, for example "7 images × 1 credit = 7 credits (2K); for a new
account the first image is free, so 6", and ask for a clear yes before rendering. Drop or swap slots the user does not want.

### 3. Check the account

Run `scripts/teruns_client.py balance`.

- Exit 0: compare `credits` and `trial_images` with the plan's cost. If `trial_images`
  is 1, the first 2K image is free: say so, and use it on the main image (slot 1) so
  the user sees the quality before paying. The trial does not cover 4K; if the user
  chose 4K and has no paid credits, offer the main image free at 2K. If credits are
  short for the rest, offer fewer slots or the top-up link from step 5.
- Exit 2 (`login_required`): run `scripts/teruns_client.py login --start --skill listing-image-set`.
  Give the user the `verify_url` and `user_code`, ask them to open it, sign in and approve.
  Then run `login --wait`. If it returns `still_pending`, wait for the user to say they
  approved and run `login --wait` again. The result shows `trial_images`.

### 4. Render, main image first

Build each prompt from `references/prompt-patterns.md`: identity lock, the slot's scene,
the text rule, the safety rule. Save each prompt to `teruns-output/<slug>/prompts/NN-slot.txt`.

Render the main image (slot 1) first:

```
python3 scripts/teruns_client.py generate --skill listing-image-set \
  --slot amazon_main --marketplace amazon.de --locale de-DE --size 2K --aspect 1:1 \
  --output-size 2000x2000 --ref /path/to/photo.jpg \
  --prompt-file teruns-output/<slug>/prompts/01-amazon_main.txt \
  --product-file teruns-output/<slug>/product.json \
  --out teruns-output/<slug>/amazon.de/01-amazon_main.png
```

Use `--output-size 2000x2000` for 2K square and `4000x4000` for 4K square; for 4:3 use
`2000x1500` / `4000x3000`. Etsy: 2000x1500 at 2K.

Open the result and compare it with the user's photo: shape, colour, parts and printed
text must match. Show it to the user and get approval before the rest. Then render the
other slots, attaching both the original photo and the approved main image
(`--ref photo.jpg --ref 01-amazon_main.png`).

Look at every image as it arrives. If the product changed, text is misspelled, or an
invented claim appears, tell the user what is wrong and offer one re-render of that slot
(it costs credits again; the fix is free only if the API refused or failed).

### 5. Handle API results

| Exit | Status | Do this |
| --- | --- | --- |
| 0 | `ok` | Continue. Note `credits_left`. |
| 2 | `login_required` | Step 3 login, then retry the same command. |
| 3 | `insufficient_credits` | If `reason` is `trial_2k_only`, offer to render this image at 2K for free instead. Otherwise show `checkout_url`. Say the remaining slots will continue after payment. When the user says they paid, run `balance`, then rerun the same command with the `--request-id` from the error output. |
| 1 | `error` | Show the error briefly. Network or 5xx: retry once with the same `--request-id` (never charged twice). `policy_violation`: rewrite the prompt. |

Never ask for card or PayPal details in chat; payment happens only on teruns.com.

### 6. Check and deliver

Run the free checker on the finished folder:

```
python3 scripts/audit_images.py teruns-output/<slug>/amazon.de --marketplace amazon.de
```

Fix any FAIL before delivering (for a main-image background or fill failure, re-render
slot 1 with a stricter scene block). Then give the user:

- the folder path and the files in slot order,
- a one-line note per image of what it shows,
- credits used and left,
- for EU stores and TikTok Shop: a reminder that AI-generated images may need disclosure
  under the marketplace's rules.

## Rules

- The product in every image must be the real product: no added features, colours,
  accessories or text.
- No marketplace badges, ratings, reviews, prices, certification marks, competitor
  brands or medical/safety claims unless the user supplies proof and asks for them.
- Only show items in "in the box" that the user listed as included.
- Do not render anything before the user approves the plan and the cost.
