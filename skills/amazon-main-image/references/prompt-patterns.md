# Prompt patterns

Every prompt sent to `teruns_client.py generate` is built from four blocks, in this order.
Write prompts in English; only the text that appears inside the image uses the target locale.

## 1. Identity lock (always first)

```
Image 1 is the exact product being sold. Reproduce it faithfully: same shape and
proportions, same colours ({color}), same materials ({material}), same parts, and the
printed text {visible_text_on_product} exactly as on the product, with no other text
on the product. Do not add, remove or redesign any part of the product.
```

When the approved main image exists, attach it as image 2 and add:
`Image 2 is the approved main image of the same product; keep the product identical to it.`

## 2. Scene (one per slot)

| Slot | Scene block |
| --- | --- |
| `amazon_main` | Single product, centered, on a pure white (#FFFFFF) seamless background with a soft natural contact shadow. The product fills about 88% of the frame on its longest side, fully in frame. Even, soft studio lighting, true-to-life colour, sharp focus. Nothing else in the image: no text, logos, badges, borders, props, hands or packaging. |
| `benefit_infographic` | Product on a clean light background, left or centre. Up to three short callouts with thin leader lines pointing to the real features: "{point1}", "{point2}", "{point3}". Large, bold, sans-serif text readable on a phone. |
| `detail_closeup` | Close-up of {feature} showing material and finish, shallow depth of field, one short label: "{label}". |
| `lifestyle` | The product in use in {setting} that suits a {audience}. Natural daylight, realistic scale, the product is the clear focal point. No text. |
| `size_dimensions` | Product front view on white with thin dimension lines and labels exactly: {dimensions}. Optional familiar object for scale only if the user approved one. |
| `comparison` | Only facts the user confirmed. Two-column layout: this product vs. "ordinary {category}", with checkmarks for: {confirmed_points}. No competitor brand names or logos. |
| `in_the_box` | Flat lay on white of exactly these items, nothing more: {included}. Small labels with item names. |
| `aplus_header` | Wide banner (970×600) with the product on one side and calm negative space for one headline: "{headline}". Brand colours {brand_colors} if given. |
| `aplus_overlay` | Wide lifestyle banner (970×300) with soft-focus area for a short overlay line: "{line}". |
| `aplus_tile` | Square tile (300×300 or 220×220) focusing on one feature: {feature}. No text unless asked. |

## 3. Text rule (when the slot has text)

```
All text drawn in the image is in {language} ({locale}). Use exactly these words and no
others: {text_list}. Spell every word correctly. No other text anywhere in the image.
```

For slots without text: `No text, letters or numbers anywhere in the image except the
product's own printed text.`

## 4. Safety rule (always last)

```
Do not show marketplace badges (such as "Best Seller" or "Amazon's Choice"), star
ratings, reviews, certification marks, prices, discounts, competitor brands, or claims
that are not listed above.
```

## Language table for in-image text

Use the store's locale (see platform-rules.md). Shopify, Etsy and TikTok Shop: ask which
language the store sells in; default en-US.
